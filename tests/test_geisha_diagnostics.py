import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend import make_handler
from geisha_archive import GeishaArchive
from geisha_diagnostics import Diagnostics


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'index.html').write_text(
            '<html><head><link rel="stylesheet" href="css/test.css"></head><body>'
            '<div id="wrapper">Test</div><script>unsafe()</script></body></html>', encoding='utf-8')
        self.log = self.root / 'technical.jsonl'
        self.diag = Diagnostics(self.log)
        self.addCleanup(self.diag.close)
        self.archive = GeishaArchive(self.root)

    def server(self, **options):
        server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
            [], self.archive, diagnostics=self.diag, **options))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        def close():
            server.shutdown()
            thread.join(3)
            server.server_close()
        self.addCleanup(close)
        return 'http://127.0.0.1:%d' % server.server_port

    def test_direct_entry_retains_asset_base_and_native_switch(self):
        base = self.server(entry='direct', native='off')
        with urlopen(base + '/ninja/wood_index.html?token=secret') as r:
            html = r.read().decode()
            self.assertEqual(r.geturl(), base + '/ninja/wood_index.html?token=secret')
            self.assertIn('<base href="/geisha/">', html)
            self.assertIn('data-native="off"', html)
            self.assertEqual(r.headers['X-zShop-Build'], self.diag.build)
            self.assertEqual(int(r.headers['Content-Length']), len(html.encode()))
            self.assertIn('no-store', r.headers['Cache-Control'])
            self.assertNotIn('unsafe()', html)

    def test_redirect_forwards_only_allowed_experiments(self):
        base = self.server()
        with urlopen(base + '/ninja/wood_index.html?zshop_native=off&zshop_css=off&token=SECRET') as r:
            self.assertTrue(r.geturl().endswith('?zshop_native=off&zshop_css=off'))
            html = r.read().decode()
            self.assertIn('data-native="off"', html)
            self.assertNotIn('<link', html)
            self.assertNotIn('<style', html)

    def test_probe_entry_has_no_archive_dependency(self):
        base = self.server(entry='probe')
        with urlopen(base + '/ninja/wood_index.html') as r:
            html = r.read().decode()
            self.assertIn('zShop display probe', html)
            self.assertIn('HTML + inline CSS OK', html)
            self.assertNotIn('css/test.css', html)

    def test_events_drop_sensitive_input_and_bound_memory(self):
        self.assertTrue(self.diag.client_event({'stage': ['dom'], 'w': ['1280'],
            'h': ['720'], 'page': ['abcdef01'], 'token': ['SECRET'],
            'url': ['https://private.invalid'], 'broken': ['-1']}))
        self.assertFalse(self.diag.client_event({'stage': ['SECRET']}))
        event = self.diag.snapshot()[-1]
        self.assertEqual(event['w'], 1280)
        self.assertNotIn('token', event)
        self.assertNotIn('broken', event)
        for _ in range(200):
            self.diag.client_event({'stage': ['load']})
        self.assertEqual(len(self.diag.snapshot()), 160)
        self.assertNotIn('SECRET', self.log.read_text())
        self.assertNotIn('private.invalid', self.log.read_text())

    def test_http_log_has_no_url_headers_address_or_account_fields(self):
        base = self.server()
        request = Request(base + '/account-secret?token=TOKEN', headers={
            'Authorization': 'Bearer CREDENTIAL', 'Cookie': 'session=COOKIE',
            'User-Agent': 'PERSONAL-UA', 'Referer': 'http://private.invalid'})
        with self.assertRaises(HTTPError):
            urlopen(request)
        with urlopen(base + '/__zshop__/status') as r:
            report = json.loads(r.read())
        text = json.dumps(report)
        for secret in ('account-secret', 'TOKEN', 'CREDENTIAL', 'COOKIE', 'PERSONAL-UA',
                       'private.invalid', '127.0.0.1', str(self.root)):
            self.assertNotIn(secret, text)
        self.assertEqual(report['events'][0]['route'], 'unknown')

    def test_head_lengths_and_event_validation(self):
        base = self.server()
        with urlopen(Request(base + '/geisha/index.html', method='HEAD')) as r:
            self.assertGreater(int(r.headers['Content-Length']), 0)
            self.assertEqual(r.read(), b'')
        with urlopen(base + '/__zshop__/event?stage=dom&w=1280&h=720') as r:
            self.assertEqual(r.headers['Content-Type'], 'image/gif')
            self.assertTrue(r.read().startswith(b'GIF89a'))
        with self.assertRaises(HTTPError) as error:
            urlopen(base + '/__zshop__/event?stage=arbitrary-secret')
        self.assertEqual(error.exception.code, 400)


if __name__ == '__main__':
    unittest.main()
