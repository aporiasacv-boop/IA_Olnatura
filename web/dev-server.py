import http.server
import json
import socketserver
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = 'http://127.0.0.1:8000'
HOST = '127.0.0.1'
PORT = 8080
PROXIED_PREFIXES = ('/ui', '/assistant', '/auth')


class PortalHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print('[portal] %s - %s' % (self.address_string(), format % args))

    def do_GET(self):
        if self._should_proxy():
            self._proxy_request('GET')
            return
        self.send_error(404)

    def do_POST(self):
        if self._should_proxy():
            self._proxy_request('POST')
            return
        self.send_error(404)

    def _should_proxy(self) -> bool:
        path = self.path.split('?', 1)[0]
        return path == '/ui' or any(path.startswith(prefix) for prefix in PROXIED_PREFIXES)

    def _proxy_request(self, method: str) -> None:
        target_url = API_BASE + self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else None
        headers = {}
        content_type = self.headers.get('Content-Type')
        if content_type:
            headers['Content-Type'] = content_type
        cookie = self.headers.get('Cookie')
        if cookie:
            headers['Cookie'] = cookie
        request = urllib.request.Request(target_url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
                self.send_response(response.status)
                for header_name in ('Content-Type', 'Set-Cookie', 'Location'):
                    header_value = response.headers.get(header_name)
                    if header_value:
                        self.send_header(header_name, header_value)
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            for header_name in ('Content-Type', 'Set-Cookie', 'Location'):
                header_value = exc.headers.get(header_name)
                if header_value:
                    self.send_header(header_name, header_value)
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


def main() -> None:
    with socketserver.ThreadingTCPServer((HOST, PORT), PortalHandler) as httpd:
        print('Portal Olnatura (proxy autenticado)')
        print('  UI:   http://%s:%s/ui' % (HOST, PORT))
        print('  API:  %s' % API_BASE)
        print('Presiona Ctrl+C para detener.')
        httpd.serve_forever()


if __name__ == '__main__':
    main()
