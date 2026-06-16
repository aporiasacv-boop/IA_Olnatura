import http.server
import json
import socketserver
import urllib.error
import urllib.request
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent / 'ui'
API_BASE = 'http://127.0.0.1:8000'
HOST = '127.0.0.1'
PORT = 8080


class PortalHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print('[portal] %s - %s' % (self.address_string(), format % args))

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path in ('/ui', '/ui/'):
            self._serve_file(UI_DIR / 'index.html', 'text/html; charset=utf-8')
            return
        if path.startswith('/ui/'):
            relative = path[len('/ui/'):]
            target = (UI_DIR / relative).resolve()
            if not str(target).startswith(str(UI_DIR.resolve())):
                self.send_error(403)
                return
            if target.is_file():
                content_type = self._content_type(target)
                self._serve_file(target, content_type)
                return
        self.send_error(404)

    def do_POST(self):
        path = self.path.split('?', 1)[0]
        if path != '/assistant':
            self.send_error(404)
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        request = urllib.request.Request(
            API_BASE + '/assistant',
            data=body,
            method='POST',
            headers={'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            self.send_header('Content-Type', exc.headers.get('Content-Type', 'application/json'))
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except urllib.error.URLError:
            detail = json.dumps({'detail': 'API no disponible en ' + API_BASE}).encode('utf-8')
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(detail)))
            self.end_headers()
            self.wfile.write(detail)

    def _serve_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _content_type(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == '.css':
            return 'text/css; charset=utf-8'
        if suffix == '.js':
            return 'application/javascript; charset=utf-8'
        if suffix == '.html':
            return 'text/html; charset=utf-8'
        if suffix == '.svg':
            return 'image/svg+xml'
        return 'application/octet-stream'


def main() -> None:
    with socketserver.ThreadingTCPServer((HOST, PORT), PortalHandler) as httpd:
        print('Portal Olnatura')
        print('  UI:  http://%s:%s/ui' % (HOST, PORT))
        print('  API: %s/assistant (proxy)' % API_BASE)
        print('Presiona Ctrl+C para detener.')
        httpd.serve_forever()


if __name__ == '__main__':
    main()
