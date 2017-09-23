"""
mock.py

Mock objects for testing
"""

import os
import re

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


class mock_error(object):

  def __init__(self, href="", name="", message=""):
    self.href = href
    self.name = name
    self.message = message


class mock_choices(dict):


  def __init__(self, choices_dict):
    # choices = {}
    # for key in choices_dict:
    #   choices[mock_choice(key)] = choices_dict[key]
    # self.choices = choices
    self.choices = choices_dict
    self.update(choices_dict)


  # def __get__(self, k):
  #   return self.choices[k]
  #
  #
  # def __set__(self, k, v):
  #   self.choices[k] = v
  #
  #
  # def __str__(self):
  #   return str(self.choices)


  def get(self, key, default=None):
    return self.choices[key] if key in self.choices else default


  def get_regex(self, regex):
    result = []
    for key, value in self.choices.items():
      if re.match(regex, key):
        result.append((key, value))
    return result


  def features(self):
    """
    TODO: This
    """
    return {}


  def patterns(self):
    """
    TODO: This
    """
    return [['test', 'test', False]]


  def numbers(self):
    """
    TODO: This
    """
    return []


# class mock_choice(object):
#
#   def __init__(self, key):
#     self.key = key
#
#
#   def iter_num(self):
#     if self.key:
#         result = re.search('[0-9]+$', self.full_key)
#         if result:
#             return int(result.group(0))
#     return None


class os_environ(object):
  """
  Helper wrapper to save, set, and reset environment variables used
  in deffile.py for testing
  """

  def __init__(self, *args, **kwargs):
    self.variables = kwargs

  def __enter__(self):
    self.old = os.environ.copy()
    for key, value in self.variables.items():
        os.environ[key] = value

  def __exit__(self, exc_type, exc_value, exc_traceback):
    os.environ = self.old
    if exc_value != None:
      return False
    return True
