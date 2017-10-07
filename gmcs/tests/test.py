"""
test.py

Utilities for testing the Grammar Matrix
"""

import os
import codecs
import tempfile
import shutil

from gmcs import deffile
from gmcs import choices

from gmcs.choices import FormData, FormInfo

# Loading
def get_path(*path):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))


def load_matrixdef(file_name):
  path = get_path("resources", "test_defs", file_name)
  return deffile.MatrixDef(path)


def load_file(path):
  with codecs.open(path, 'r', encoding="utf-8") as f:
    return f.read()


def load_testhtml(file_name):
  path = get_path("resources", "test_html", file_name + ".html")
  return load_file(path)


def load_subpage(file_name):
  path = get_path("resources", "sub_page_regression_tests", file_name + ".html")
  return load_file(path)


def load_choices(file_name):
  # "gmcs/tests/resources/test_choices/iter_choices.txt"
  path = get_path("resources", "test_choices", file_name)
  return choices.ChoicesFile(path)


# Comparing
def remove_empty_lines(string):
  return [line for line in [line.strip() for line in string.split("\n")] if line]


# Debugging
def print_both(actual, expected):
  print("#"*50 + " ACTUAL " + "#"*50)
  print(actual)
  print
  print("#"*50 + " EXPECTED " + "#"*50)
  print(expected)


def save_both(actual, expected):
  save(actual, "actual.txt")
  save(expected, "expected.txt")


def save(text, location):
  with codecs.open(location, 'w+', encoding='UTF-8') as f:
    f.write(text)


class choice_environ(object):
  """
  Save the specified choices file to a temporary file for testing functions
  which take file objects

  TODO: Merge this with environ_choices???
  """

  def __init__(self, section, test_choices_file, path=["gmcs", "tests", "resources", "test_choices"]):
    self.path = path

    self.form_data = FormData()
    self.form_data['section'] = FormInfo('section', section)

    test_choices = load_file(os.path.join(*(path + [test_choices_file])))
    self.choices_file = tempfile.NamedTemporaryFile(mode='w+')
    self.choices_file.write(test_choices)
    self.choices_file.seek(0)


  def __enter__(self):
    return self


  def __exit__(self, *args, **kwargs):
    self.choices_file.close()


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


class environ_choices(object):
  """
  Helper wrapper to temporarily store choices file in session
  TODO: Conjoin this with choice_environ???
  """

  def __init__(self, choices_file, path=["gmcs", "tests", "resources", "test_choices"]):
    self.choices = os.path.join(*(path + [choices_file]))


  def __enter__(self):
    session = os.environ['HTTP_COOKIE']
    if not session:
      raise Exception("Could not find directory to set temporary choices: %s" % session)
    session = session.split("=")[-1]
    self.temp = os.path.join("sessions", session, "choices")
    if not os.path.exists(os.path.join("sessions", session)):
      os.mkdir(os.path.join("sessions", session))
    shutil.copy(self.choices, self.temp)


  def __exit__(self, exc_type, exc_value, exc_traceback):
    os.remove(self.temp)
