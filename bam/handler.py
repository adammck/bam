#!/usr/bin/env python
# vim: et ts=2 sw=2

import BaseHTTPServer

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    resp = self.app().request(self.path, dict(self.headers))
    if resp:

      self.send_response(resp.status)

      for header in resp.getheaders():
        self.send_header(*header)

      self.end_headers()
      self.wfile.write(resp.read())

  def app(self):
    """Return an app instance to handle this request."""
    return self.server.app(self.hostname())

  def hostname(self):
    """Return the bare hostname of this request."""
    return self.netloc().split(":")[0]

  def netloc(self):
    """Return the netloc (host:port) of this request."""
    return self.headers.getheader("host")

  # Silence the request log.
  def log_message(self, format, *args):
    pass
