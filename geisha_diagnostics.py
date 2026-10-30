"""Bounded, anonymous diagnostics. Never retain request URLs or headers."""
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from threading import Lock

CODE_FILES = ('backend.py', 'geisha_archive.py', 'geisha_preview_renderer.py',
              'geisha_diagnostics.py', 'geisha_readonly_navigation.py', 'zshop_bridge.js')
STAGES = frozenset(('bridge', 'dom', 'load', 'script-error', 'native-off',
                    'browser-missing', 'browser-error', 'startup-before',
                    'startup-ok', 'startup-error', 'startup-missing',
                    'unlock-before', 'unlock-ok', 'unlock-error', 'unlock-missing'))
NUMBERS = frozenset(('w', 'h', 'visible', 'images', 'broken', 'vw', 'vh'))
PIXEL = bytes.fromhex('47494638396101000100800000000000ffffff21f90401000000002c'
                      '00000000010001000002024401003b')


def build_id():
    digest = sha256()
    for name in CODE_FILES:
        digest.update(name.encode('ascii'))
        # Same ID in a Windows ZIP checkout and Linux CI.
        digest.update((Path(__file__).parent / name).read_bytes().replace(b'\r\n', b'\n'))
    return digest.hexdigest()[:16]


def route_kind(path):
    if path in ('/', '/ninja/wood_index.html', '/geisha', '/geisha/'):
        return 'entry'
    if path == '/geisha/index.html':
        return 'home'
    if path == '/geisha/zshop-bridge.js':
        return 'bridge'
    if path.startswith('/__zshop__/') or path in ('/health', '/healthz'):
        return 'diagnostic'
    if path.startswith('/geisha/'):
        suffix = Path(path).suffix.lower()
        return {'.css': 'css', '.html': 'page', '.png': 'image', '.jpg': 'image',
                '.gif': 'image', '.woff': 'font', '.ttf': 'font'}.get(suffix, 'asset')
    return 'unknown'


class Diagnostics:
    def __init__(self, log_path=None):
        self.build = build_id()
        self.events = deque(maxlen=160)
        self.lock = Lock()
        self.log = open(log_path, 'a', encoding='utf-8') if log_path else None

    def record(self, **fields):
        event = {'time': datetime.now(timezone.utc).isoformat(timespec='milliseconds'),
                 'build': self.build, **fields}
        with self.lock:
            self.events.append(event)
            if self.log:
                self.log.write(json.dumps(event, sort_keys=True) + '\n')
                self.log.flush()

    def client_event(self, params):
        stage = params.get('stage', [''])[0]
        if stage not in STAGES:
            return False
        fields = {'kind': 'client', 'stage': stage}
        page = params.get('page', [''])[0]
        if len(page) == 8 and all(c in '0123456789abcdef' for c in page):
            fields['page'] = page
        for name in NUMBERS:
            value = params.get(name, [''])[0]
            if value.isascii() and value.isdigit() and len(value) <= 5:
                fields[name] = min(int(value), 32768)
        self.record(**fields)
        return True

    def snapshot(self):
        with self.lock:
            return list(self.events)

    def close(self):
        if self.log:
            self.log.close()


def probe_html(bridge_tag, build):
    # Independent of the archive and CSS. Deliberately a labelled test page.
    return ('''<!doctype html><html><head><meta charset="utf-8">
<title>zShop display probe</title></head>
<body style="margin:0;background:#17324d;color:white;font:28px sans-serif">
<h1>zShop display probe</h1><p>Build: %s</p>
<div id="wrapper" style="width:640px;height:240px;background:#008850">
HTML + inline CSS OK<br><span style="background:#d05000">Orange block</span></div>
<p id="zshop-probe-state">JavaScript pending</p>
<p><a style="color:white" href="/geisha/index.html">Open local Geisha</a></p>
%s</body></html>''' % (build, bridge_tag)).encode('utf-8')
