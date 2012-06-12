#!/usr/bin/env python
# vim: et ts=2 sw=2

import BaseHTTPServer
import bam

class Server(BaseHTTPServer.HTTPServer):
  counter = 0
  pool = {}

  def app(self, name):
    if name not in self.pool:
      port = self.next_port()
      self.pool[name] = bam.App(name, port)

    return self.pool[name]

  def next_port(self):
    self.counter += 1
    base_port = self.server_address[1]
    return base_port + self.counter
