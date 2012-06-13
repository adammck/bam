#!/usr/bin/env python
# vim: et ts=2 sw=2

import unittest
import bam

TEST_HOST = "localhost"
TEST_PORT = 40559

class MockHandler(object):
  pass

class TestServer(unittest.TestCase):

  def setUp(self):
    self.server = bam.Server((TEST_HOST, TEST_PORT), MockHandler)

  def tearDown(self):
    self.server.socket.close()

  def test_app(self):
    app_a1 = self.server.app('a')
    app_a2 = self.server.app('a')
    app_b1 = self.server.app('b')
    self.assertEqual(app_a1, app_a2)
    self.assertNotEqual(app_a1, app_b1)

  def test_next_port(self):
    ports = set([self.server.next_port() for n in range(10)])
    self.assertNotIn(TEST_PORT, ports)
    self.assertEqual(len(ports), 10)
