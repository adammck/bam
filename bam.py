#!/usr/bin/env python
# vim: et ts=2 sw=2

import BaseHTTPServer
import subprocess
import httplib
import envoy
import socket
import time
import sys
import os

PORT = 30559


class App(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.proc = None

  @property
  def cmd(self):
    """Return the command to start this app."""
    return "%s manage.py runserver %d" % (self.python, self.port)

  @property
  def python(self):
    """Return the absolute path to the Python interpreter for this app."""

    if self.venv:
      return "%s/bin/python" % self.venv

    else:
      return "python"

  @property
  def venv(self):
    """
    Return the path to the virtualenv for this app, as specified by the `.venv`
    file in the project root. Return `None` if the file doesn't exist.
    """

    filename = "%s/.venv" % self.root

    if os.path.exists(filename):
      venv = open(filename).read().strip()
      return os.path.expanduser(venv)

  @property
  def root(self):
    """Return the real root directory of this app."""
    return os.path.expanduser("~/.bam/%s" % self.name)

  @property
  def name(self):
    """Return the name (hostname minus the TLD) of this app."""
    return self.host.rsplit(".", 1)[0]

  def start(self):
    print "Starting %r on %r in venv %r" % (self.name, self.port, self.venv)
    self.proc = self._connect(self.cmd, cwd=self.root)

  def stop(self):
    self.proc.kill()
    self.proc = None

  def is_running(self):
    """Return `True` if this app is currently running."""
    return self.proc and (self.proc.status_code is None)

  def request(self, path, headers):
    """
    Perform an HTTP request against this app, starting it if necessary. Return
    an `httplib.HTTPResponse` object, or `None` if the app can't be reached.
    """

    if not self.is_running():
      self.start()

    failures = 0

    headers["X-Forwarded-Host"] = self.host
    headers["X-Forwarded-Server"] = self.host

    while True:
      try:
        conn = httplib.HTTPConnection("localhost", self.port)
        conn.request("GET", path, headers=headers)
        return conn.getresponse()

      # If the port isn't open yet, keep on trying. The server probably hasn't
      # warmed up yet. Give up if it doesn't work out within a few seconds.
      except socket.error, e:
        if (e.errno == 61) and (failures < 5):
          failures += 1
          time.sleep(1)

        else:
          return None

  # Subprocesses are handled by Envoy, for now. I'm probably going to remove it
  # and work directly with the subprocess interface, because it isn't nearly as
  # painful as I remember.
  def _connect(self, command, data=None, env=None, cwd=None):
    command_str = envoy.expand_args(command).pop()

    proc = subprocess.Popen(
      command_str,
      cwd=cwd,
      env=dict(),
      stdin=None,
      stdout=open("%s/bam.stdout.log" % cwd, "w"),
      stderr=open("%s/bam.stderr.log" % cwd, "w"))

    return envoy.ConnectedCommand(process=proc)


class Server(BaseHTTPServer.HTTPServer):
  counter = 0
  pool = {}

  def app(self, name):
    if name not in self.pool:
      port = PORT + self.next_port()
      self.pool[name] = App(name, port)

    return self.pool[name]

  def next_port(self):
    self.counter += 1
    return self.counter


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


if __name__ == "__main__":
  server_address = ('127.0.0.1', PORT)
  httpd = Server(server_address, Handler)
  httpd.serve_forever()
