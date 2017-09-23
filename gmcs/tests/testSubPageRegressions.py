import unittest

import os
import re
import codecs

from gmcs import html
from gmcs import deffile
from gmcs.choices import ChoicesFile
from gmcs.deffile import MatrixDefSyntaxException

from mock import mock_choices, mock_validation, mock_error, os_environ


def get_path(*path):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))


def load_expected(file_name):
  path = get_path("resources", "sub_page_regression_tests", file_name + ".html")
  with codecs.open(path, 'r', encoding="utf-8") as f:
    return f.read()


def remove_empty_lines(string):
  return "\n".join((line.strip() for line in string.split("\n") if line.strip()))


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


### TESTS
class RegressionTests(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls._definition = deffile.MatrixDef("web/matrixdef")


  def testCase(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('case', '7777', mock_validation())
      expected = load_expected("case")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testGender(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('gender', '7777', mock_validation())
      expected = load_expected("gender")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testTAM(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('tense-aspect-mood', '7777', mock_validation())
      expected = load_expected("TAM")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testGeneral(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('general', '7777', mock_validation())
      expected = load_expected("general")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testWordOrder(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('word-order', '7777', mock_validation())
      expected = load_expected("word-order")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testNumber(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('number', '7777', mock_validation())
      expected = load_expected("number")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testPerson(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('person', '7777', mock_validation())
      expected = load_expected("person")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testDirectInverse(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('direct-inverse', '7777', mock_validation())
      expected = load_expected("direct-inverse")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testOtherFeatures(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('other-features', '7777', mock_validation())
      expected = load_expected("other-features")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSententialNegation(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('sentential-negation', '7777', mock_validation())
      expected = load_expected("sentential-negation")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testCoordination(self):
    """
    TODO: Confirm this... seems like it might be wrong
    """
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('coordination', '7777', mock_validation())
      expected = load_expected("coordination")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMatrixYesNo(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('matrix-yes-no', '7777', mock_validation())
      expected = load_expected("matrix-yes-no")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testInformationStructure(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('info-str', '7777', mock_validation())
      expected = load_expected("info-str")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testArgumentOptionality(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('arg-opt', '7777', mock_validation())
      expected = load_expected("arg-opt")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testLexicon(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('lexicon', '7777', mock_validation())
      expected = load_expected("lexicon")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMorphology(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('morphology', '7777', mock_validation())
      expected = load_expected("morphology")
      save_both(actual, expected)
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))
