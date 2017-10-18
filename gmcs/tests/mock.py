"""
mock.py

Mock objects for testing
"""

import re

from gmcs.choices import ChoicesFile, ChoiceDict

class mock_validation(object):

  def __init__(self, infos={}, warnings={}, errors={}):
    self.infos = infos
    self.warnings = warnings
    self.errors = errors


  def has_errors(self):
    return bool(self.errors)


  def has_warnings(self):
    return bool(self.warnings)


  def has_infos(self):
    return bool(self.infos)


  def err(self, key, message, anchor=None, concat=True):
    self.errors[key] = mock_error(message=message)


  def warn(self, key, message, anchor=None, concat=True):
    self.warnings[key] = mock_error(message=message)


  def info(self, key, message, anchor=None, concat=True):
    self.infos[key] = mock_error(message=message)


class mock_error(object):

  def __init__(self, href="", name="", message=""):
    self.href = href
    self.name = name
    self.message = message


def mock_choices(choices=tuple()):
  result = ChoicesFile()
  for key, value in choices:
    result[key] = value
  return result
