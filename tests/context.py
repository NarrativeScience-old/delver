# flake8: noqa F401
"""Provide context to the test runner.

Allows for running the tests without requiring the package to be installed. See
http://docs.python-guide.org/en/latest/writing/structure/#test-suite
for more information.
"""
import os
import sys

import delver.core as core
import delver.delve as delve
import delver.exceptions as exceptions
import delver.handlers as handlers

sys.path.insert(0, os.path.abspath(".."))
