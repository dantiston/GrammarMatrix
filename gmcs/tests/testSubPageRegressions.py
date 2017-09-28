#!usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest

import os
import re
import codecs

from gmcs import html
from gmcs import deffile
from gmcs.choices import ChoicesFile
from gmcs.deffile import MatrixDefSyntaxException

from mock import mock_choices, mock_validation, mock_error, os_environ, environ_choices
from test import load_subpage, remove_empty_lines

from test import save_both

### TESTS
class RegressionTests(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls._definition = deffile.MatrixDef("web/matrixdef")


  def testCase(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('case', '7777', mock_validation())
      expected = load_subpage("case")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testGender(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('gender', '7777', mock_validation())
      expected = load_subpage("gender")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testTAM(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('tense-aspect-mood', '7777', mock_validation())
      expected = load_subpage("TAM")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testGeneral(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('general', '7777', mock_validation())
      expected = load_subpage("general")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testWordOrder(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('word-order', '7777', mock_validation())
      expected = load_subpage("word-order")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testNumber(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('number', '7777', mock_validation())
      expected = load_subpage("number")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testPerson(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('person', '7777', mock_validation())
      expected = load_subpage("person")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testDirectInverse(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('direct-inverse', '7777', mock_validation())
      expected = load_subpage("direct-inverse")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testOtherFeatures(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('other-features', '7777', mock_validation())
      expected = load_subpage("other-features")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSententialNegation(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('sentential-negation', '7777', mock_validation())
      expected = load_subpage("sentential-negation")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testCoordination(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('coordination', '7777', mock_validation())
      expected = load_subpage("coordination")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMatrixYesNo(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('matrix-yes-no', '7777', mock_validation())
      expected = load_subpage("matrix-yes-no")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testInformationStructure(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('info-str', '7777', mock_validation())
      expected = load_subpage("info-str")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testArgumentOptionality(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('arg-opt', '7777', mock_validation())
      expected = load_subpage("arg-opt")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testLexicon(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('lexicon', '7777', mock_validation())
      expected = load_subpage("lexicon")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testLexicon_Choices(self):
    with os_environ(HTTP_COOKIE="session=7777"), environ_choices("lexicon_choices.txt"):
      actual = self._definition.sub_page('lexicon', '7777', mock_validation())
      expected = load_subpage("lexicon_choices")
      save_both(actual, expected)
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMorphology(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      actual = self._definition.sub_page('morphology', '7777', mock_validation())
      expected = load_subpage("morphology")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))
