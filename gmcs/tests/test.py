"""
test.py

Utilities for testing the Grammar Matrix
"""

import os
import codecs

from gmcs import deffile
from gmcs import choices

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
