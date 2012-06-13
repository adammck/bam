#!/usr/bin/env python
# vim: et ts=2 sw=2

import unittest
import os
import bam

TEST_PORT = 40559
TEST_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_VENV = "/tmp/bam-mock-venv"

TEST_VARS_FILE = "A=1\nB=2\n"
TEST_VARS = {"A": "1", "B": "2"}

class TestApp(unittest.TestCase):

  def setUp(self):
    self.simple_app    = bam.App("simple.bam",    TEST_PORT+1, TEST_ROOT)
    self.app_with_venv = bam.App("with_venv.bam", TEST_PORT+2, TEST_ROOT)
    self.app_with_vars = bam.App("with_vars.bam", TEST_PORT+3, TEST_ROOT)

  def test_cmd(self):
    self.assertEqual("manage.py runserver %d" % self.simple_app.port, self.simple_app.cmd)

  def test_python(self):
    self.assertEqual(self.simple_app.python,    "python")
    self.assertEqual(self.app_with_venv.python, "%s/bin/python" % TEST_VENV)

  def test_venv(self):
    self.assertEqual(self.simple_app.venv,    None)
    self.assertEqual(self.app_with_venv.venv, TEST_VENV)

  def test_environment(self):
    self.assertEqual({ },       self.simple_app.environment)
    self.assertEqual(TEST_VARS, self.app_with_vars.environment)

  def test_path(self):
    self.assertEqual(os.path.join(TEST_ROOT, "simple"), self.simple_app.path)

  def test_name(self):
    self.assertEqual("simple", self.simple_app.name)

  def test_parse_env(self):
    self.assertEqual(TEST_VARS, self.simple_app._parse_env(TEST_VARS_FILE))
