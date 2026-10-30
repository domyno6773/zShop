"""Render a LOCAL Geisha archive and check actual HTTP, DOM and native failures.

Requires playwright plus an installed browser. No source assets are copied.
Reports/screenshots stay in the explicitly chosen output directory.
"""
import argparse
import json
from pathlib import Path
import sys
import threading
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import load_catalog, make_handler
from geisha_archive import GeishaArchive
from geisha_diagnostics import Diagnostics


def check_archive(directory, output, engine='chromium', channel=None):
    from playwright.sync_api import sync_playwright
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog(ROOT / 'catalog.example.json')
    archive = GeishaArchive(directory, catalog)
    report = {'archive': archive.summary(), 'engine': engine, 'cases': []}
    cases = (
        ('home', 'redirect', 'all', True, 1280, 720, None, '/ninja/wood_index.html'),
        ('small-viewport', 'redirect', 'all', True, 854, 480, None, '/ninja/wood_index.html'),
        ('javascript-disabled', 'redirect', 'all', True, 1280, 720, 'no-js', '/geisha/index.html'),
        ('startup-throws', 'redirect', 'all', True, 1280, 720, 'throw', '/geisha/index.html'),
        ('native-off', 'redirect', 'off', True, 1280, 720, 'forbid', '/geisha/index.html'),
        ('direct-entry', 'direct', 'all', True, 1280, 720, None, '/ninja/wood_index.html'),
        ('without-css', 'redirect', 'off', False, 1280, 720, None, '/geisha/index.html'),
        ('probe', 'probe', 'all', True, 1280, 720, None, '/ninja/wood_index.html'),
        ('startup-only', 'redirect', 'startup', True, 1280, 720, 'success', '/geisha/index.html'),
        ('unlock-only', 'redirect', 'unlock', True, 1280, 720, 'success', '/geisha/index.html'),
        ('methods-missing', 'redirect', 'all', True, 1280, 720, 'missing', '/geisha/index.html'),
    )
    for name in ('always02_01.html', 'shelf02_01.html'):
        if (archive.root / name).is_file():
            cases += ((name, 'redirect', 'all', True, 1280, 720, None, '/geisha/' + name),)
    with sync_playwright() as p:
        launch = {'headless': True}
        if channel:
            launch['channel'] = channel
        browser = getattr(p, engine).launch(**launch)
        report['browser_version'] = browser.version
        for label, entry, native, css, width, height, mock, route in cases:
            diag = Diagnostics()
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
                catalog, archive, diagnostics=diag, entry=entry, native=native, css=css))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            origin = 'http://127.0.0.1:%d' % server.server_port
            context = browser.new_context(viewport={'width': width, 'height': height},
                                          java_script_enabled=mock != 'no-js')
            page = context.new_page()
            item = {'name': label, 'requests': [], 'errors': [], 'failures': []}
            def response_received(response):
                item['requests'].append({'path': urlsplit(response.url).path,
                                         'status': response.status,
                                         'type': response.headers.get('content-type'),
                                         'local': response.url.startswith(origin + '/')})
            page.on('response', response_received)
            page.on('pageerror', lambda error: item['errors'].append(str(error)))
            page.on('requestfailed', lambda request: item['failures'].append(urlsplit(request.url).path))
            if mock == 'throw':
                page.add_init_script('''window.nativeCalls=[];window.wiiuBrowser={
                    endStartUp:function(x){nativeCalls.push(['startup',x]);throw Error('test');},
                    lockHomeButtonMenu:function(x){nativeCalls.push(['unlock',x]);}};''')
            elif mock == 'forbid':
                page.add_init_script('''Object.defineProperty(window,'wiiuBrowser',{
                    get:function(){throw Error('native access forbidden');}});''')
            elif mock == 'success':
                page.add_init_script('''window.nativeCalls=[];window.wiiuBrowser={
                    endStartUp:function(x){nativeCalls.push(['startup',x]);},
                    lockHomeButtonMenu:function(x){nativeCalls.push(['unlock',x]);}};''')
            elif mock == 'missing':
                page.add_init_script('window.wiiuBrowser={};')
            try:
                response = page.goto(origin + route, wait_until='networkidle')
                item['status'] = response.status
                item['build'] = response.headers.get('x-zshop-build')
                item['dom'] = page.evaluate('''() => {
                    var e=document.getElementById('wrapper'), r=e.getBoundingClientRect();
                    var c=getComputedStyle(e);return {display:c.display,visibility:c.visibility,
                    opacity:c.opacity,x:r.x,y:r.y,width:r.width,height:r.height,
                    images:Array.from(document.images).map(i=>({ok:i.complete&&i.naturalWidth>0})),
                    scripts:Array.from(document.scripts).map(s=>s.getAttribute('src')),
                    replacementCharacters:document.documentElement.textContent.split('\ufffd').length-1};}''')
                page.screenshot(path=str(output / (label + '.png')))
                item['events'] = diag.snapshot()
                dom = item['dom']
                assert response.status == 200, 'HTML not 200'
                assert response.headers['cache-control'] == 'no-store', 'HTML cached'
                assert dom['width'] > 0 and dom['height'] > 0, 'hidden wrapper'
                assert dom['visibility'] == 'visible' and float(dom['opacity']) > 0, 'invisible wrapper'
                assert dom['scripts'] == ['/geisha/zshop-bridge.js'], 'unexpected script'
                assert not item['errors'], 'uncaught JS exception'
                assert not item['failures'], 'failed request'
                assert all(r['local'] for r in item['requests']), 'remote response'
                assert all(r['status'] == 200 or (r['status'] == 302 and
                           r['path'] == '/ninja/wood_index.html' and entry == 'redirect')
                           for r in item['requests'] if r['path'] != '/favicon.ico'), 'bad asset status'
                assert all(i['ok'] for i in dom['images']), 'broken image'
                if mock == 'throw':
                    assert page.evaluate('window.nativeCalls') == [['startup', True], ['unlock', False]], 'HOME not unlocked'
                    stages = [e.get('stage') for e in item['events']]
                    assert 'startup-error' in stages and 'unlock-ok' in stages, 'missing error diagnostics'
                if mock == 'forbid':
                    assert any(e.get('stage') == 'native-off' for e in item['events']), 'native off ignored'
                if mock == 'success':
                    expected = [['startup', True]] if native == 'startup' else [['unlock', False]]
                    assert page.evaluate('window.nativeCalls') == expected, 'native isolation failed'
                if mock == 'missing':
                    stages = [e.get('stage') for e in item['events']]
                    assert 'startup-missing' in stages and 'unlock-missing' in stages
                item['passed'] = True
            except Exception as error:
                item['passed'] = False
                item['reason'] = str(error)
            finally:
                context.close()
                server.shutdown()
                thread.join(3)
                server.server_close()
                diag.close()
            report['cases'].append(item)
        browser.close()
    (output / 'browser-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('--output', required=True)
    parser.add_argument('--engine', choices=('chromium', 'webkit'), default='chromium')
    parser.add_argument('--channel', help='Installed Chromium channel, e.g. msedge')
    args = parser.parse_args()
    report = check_archive(args.directory, args.output, args.engine, args.channel)
    for case in report['cases']:
        print(('PASS' if case['passed'] else 'FAIL'), case['name'], case.get('reason', ''))
    raise SystemExit(0 if all(c['passed'] for c in report['cases']) else 1)


if __name__ == '__main__':
    main()
