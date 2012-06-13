#!/usr/bin/env python
# vim: et ts=2 sw=2

import subprocess
import httplib
import envoy
import socket
import time
import os

class App(object):
  def __init__(self, host, port, root="~/.bam"):
    self.host = host
    self.port = port
    self.root = root
    self.proc = None

  @property
  def cmd(self):
    """Return the command to start this app, excluding the Python interpreter."""
    return "manage.py runserver %d" % (self.port)

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

    filename = "%s/.venv" % self.path

    if os.path.exists(filename):
      venv = open(filename).read().strip()
      return os.path.expanduser(venv)

  @property
  def environment(self):
    filename = "%s/.bam-vars" % self.path

    try:
      with open(filename) as f:
        return self._parse_env(f.read())

    except:
      return { }

  @property
  def path(self):
    """Return the path to this app."""
    return os.path.join(os.path.expanduser(self.root), self.name)

  @property
  def name(self):
    """Return the name (hostname minus the TLD) of this app."""
    return self.host.rsplit(".", 1)[0]

  def _parse_env(self, env_str):
    """Parse an environment file (typically `.bam-env`) into a dict."""

    env = {}

    for line in env_str.strip().split():
      key, val = line.split("=", 1)
      env[key] = val

    return env

  def start(self):
    print "Starting %r on %r in venv %r with env %r" % (self.name, self.port, self.venv, self.environment)
    self.proc = self._connect("%s %s" % (self.python, self.cmd), cwd=self.path)

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
      env=self.environment,
      stdin=None,
      stdout=open("%s/bam.stdout.log" % cwd, "w"),
      stderr=open("%s/bam.stderr.log" % cwd, "w"))

    return envoy.ConnectedCommand(process=proc)
