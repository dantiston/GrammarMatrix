#!usr/bin/env python2.7
# -*- coding: utf-8 -*-

import unittest

import os
import re
import shutil

import StringIO

from gmcs import html
from gmcs import deffile
from gmcs.deffile import MatrixDefSyntaxException
from gmcs.choices import FormInfo

from mock import mock_choices, mock_validation, mock_error
from test import load_testhtml, load_matrixdef, load_choices, remove_empty_lines, load_file, os_environ, choice_environ

from test import save_both, print_both

"""
TODO:
    test MatrixDef.get_iter_lines()
    test deffile.tokenize_def_line
"""

# For seeing actual output
# def assertEqual(self, actual, expected):
#   if expected != actual:
#     print
#     print "#" * 20, "EXPECTED", "#" * 20
#     print expected
#     print "#" * 20, "ACTUAL", "#" * 20
#     print actual
#     print
#   super(InitializerTests, self).assertEqual(expected, actual)

### TESTS
class InitializerTests(unittest.TestCase):

  def testInitializer_Basic(self):
    definition = load_matrixdef("testBasic")
    self.assertEqual(definition.tokenized_lines, [(['Section', 'test-basic', 'Test Basic', 'TestBasic'], 4, 'Section'), (['Label', '<p>Test</p>'], 2, 'Label'), (['Separator'], 1, 'Separator'), (['Label', '<p>Test</p>'], 2, 'Label')])
    self.assertEqual(definition.sections, {'test-basic': [(['Section', 'test-basic', 'Test Basic', 'TestBasic'], 4, 'Section'), (['Label', '<p>Test</p>'], 2, 'Label'), (['Separator'], 1, 'Separator'), (['Label', '<p>Test</p>'], 2, 'Label')]})
    self.assertEqual(definition.section_names, {'test-basic':'Test Basic'})
    self.assertEqual(definition.doc_links, {'test-basic':'TestBasic'})


  def testInitializer_MultipleSections(self):
    definition = load_matrixdef("testMultipleSections")
    self.assertEqual(definition.tokenized_lines, [([u'Section', u'test-basic', u'Test Basic', u'TestBasic'], 4, u'Section'), ([u'Label', u'<p>Test</p>'], 2, u'Label'), ([u'Section', u'test-basic-2', u'Test Basic 2', u'TestBasic2'], 4, u'Section'), ([u'Label', u'<p>Test2</p>'], 2, u'Label')])
    self.assertEqual(definition.sections, {'test-basic': [([u'Section', u'test-basic', u'Test Basic', u'TestBasic'], 4, u'Section'), ([u'Label', u'<p>Test</p>'], 2, u'Label')], u'test-basic-2': [([u'Section', u'test-basic-2', u'Test Basic 2', u'TestBasic2'], 4, u'Section'), ([u'Label', u'<p>Test2</p>'], 2, u'Label')]})
    self.assertEqual(definition.section_names, {'test-basic': 'Test Basic', 'test-basic-2': 'Test Basic 2'})
    self.assertEqual(definition.doc_links, {'test-basic': 'TestBasic', 'test-basic-2': 'TestBasic2'})


  def testInitializer_Comments(self):
    definition = load_matrixdef("testBasicCommented")
    self.assertEqual(definition.tokenized_lines, [(['Section', 'test-basic', 'Test Basic', 'TestBasic'], 4, 'Section'), (['Label', '<p>Test</p>'], 2, 'Label'), (['Separator'], 1, 'Separator'), (['Label', '<p>Test</p>'], 2, 'Label')])
    self.assertEqual(definition.sections, {'test-basic': [(['Section', 'test-basic', 'Test Basic', 'TestBasic'], 4, 'Section'), (['Label', '<p>Test</p>'], 2, 'Label'), (['Separator'], 1, 'Separator'), (['Label', '<p>Test</p>'], 2, 'Label')]})
    self.assertEqual(definition.section_names, {'test-basic':'Test Basic'})
    self.assertEqual(definition.doc_links, {'test-basic':'TestBasic'})



class TokenizeDefLineTests(unittest.TestCase):

  def testTokenizeDefLine_minimal(self):
    actual = deffile.tokenize_def_line("Separator")
    expected = ["Separator"]
    self.assertEqual(actual, expected)


  def testTokenizeDefLine_basic(self):
    actual = deffile.tokenize_def_line("EndIter test")
    expected = ["EndIter", "test"]
    self.assertEqual(actual, expected)


  def testTokenizeDefLine_quoted(self):
    actual = deffile.tokenize_def_line("Check test-name \"Test Name\"")
    expected = ["Check", "test-name", "Test Name"]
    self.assertEqual(actual, expected)


  def testTokenizeDefLine_quoted_empty(self):
    actual = deffile.tokenize_def_line("Check test-name \"Test Name\" \"\"")
    expected = ["Check", "test-name", "Test Name", ""]
    self.assertEqual(actual, expected)


  def testTokenizeDefLine_quoted_escaped(self):
    actual = deffile.tokenize_def_line("Check test-name \"Test \\\"Name\\\"\"")
    expected = ["Check", "test-name", "Test \"Name\""]
    self.assertEqual(actual, expected)


class DefsToHtmlTests(unittest.TestCase):
  """
  NOTE: defs_to_html() expects input lines to be stripped

  TODO: Tests for conditional skipping
  TODO: Tests for striking options from select and multiselect

  TODO: These still need tests
  BeginIter: self.iter_to_html
  """

  @classmethod
  def setUpClass(cls):
    cls._definition = deffile.MatrixDef(None)


  def testDefsToHtml_cache(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Cache nouns noun[0-9]+$ name"
      #tokenized_lines = [['Cache', 'nouns', 'noun[0-9]+$', 'name']]
      tokenized_lines = [(['Cache', 'nouns', 'noun[0-9]+$', 'name'], 4, 'Cache')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}}), mock_validation(), "", {})
      expected = '<script type="text/javascript">\n// A cache of choices from other subpages\nvar nouns = [\n\'test-noun:noun1\',\n];\n</script>'
      self.assertEqual(actual, expected)


  @unittest.skip("Need to figure out how choices object is structured and enhance mock_choices object")
  def testDefsToHtml_iter(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [(['BeginIter', 'test{i}', '"test-iter"'], 3, 'BeginIter'), (['Text', 'name', 'Test variable: {i}', "", "", "20"], 6, 'Text'), (['EndIter', 'test'], 2, 'EndIter')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({}), mock_validation(), "", {})
      expected = ''
      self.assertEqual(actual, expected)


  @unittest.skip("Need to figure out how choices object is structured and enhance mock_choices object")
  def testDefsToHtml_iter_choices(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [['BeginIter', 'test{i}', '"test-iter"'], ['Text', 'name', 'Test variable: {i}', "", "", "20"], ['EndIter', 'test']]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}, "test":{"name":"test-test"}}), mock_validation(), "", {})
      expected = ''
      self.assertEqual(actual, expected)


  @unittest.skip("Need to figure out how choices object is structured and enhance mock_choices object")
  def testDefsToHtml_iter_cookie(self):
    """
    Test the functionality which checks for css in the cookie
    """
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [['BeginIter', 'test{i}', '"test-iter"'], ['Text', 'name', 'Test variable: {i}', "", "", "20"], ['EndIter', 'test']]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}, "test":{"name":"test-test"}}), mock_validation(), "", {})
      expected = ''
      self.assertEqual(actual, expected)


  def testDefsToHtml_label(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Label "<p>Test</p>"
      tokenized_lines = [(['Label', '<p>Test</p>'], 2, 'Label')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Test</p>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_separator(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Separator
      tokenized_lines = [(['Separator'], 1, 'Separator')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<hr>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_button(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Button test-button "<p>Test Button: " "</p>" ""
      tokenized_lines = [(['Button', 'test-button', '<p>Test Button: ', '</p>', ''], 5, 'Button')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Test Button: <input type="button"  value="test-button"></p>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_check(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Check test-check "test-check" "check: " "" "testMe();"
      tokenized_lines = [(['Check', 'test-check', 'test-check', 'check: ', '', 'testMe();'], 6, 'Check')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<label>check: <input type="checkbox"  name="test-check" onclick="testMe();"></label>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_file(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # File test-file "test file" "<p>Test file: </p>" ""
      tokenized_lines = [(['File', 'test-file', 'test file', '<p>Test file: </p>', ''], 5, 'File')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Test file: </p><input type="file"  name="test-file">\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_hidden(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Hidden test-hidden "test hidden"
      tokenized_lines = [(['Hidden', 'test-hidden', 'test hidden'], 3, 'Hidden')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<input type="hidden"  name="test-hidden">\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_radio(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Radio test-radio \"test radio\" \"\" \"\"", ". test-bullet1 \"hello\" \"\" \"\" \"\"", ". test-bullet2 \"world\" \"\" \"\" \"\""
      tokenized_lines = [(['Radio', 'test-radio', 'test radio', '', ''], 5, 'Radio'), (['.', 'test-bullet1', 'hello', '', '', ''], 6, '.'), (['.', 'test-bullet2', 'world', '', '', ''], 6, '.')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<label><input type="radio"  name="test-radio" value="test-bullet1"></label>\n<label><input type="radio"  name="test-radio" value="test-bullet2"></label>\n\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Select test-select \"test select\" \"\" \"<br />\""
      tokenized_lines = [(['Select', 'test-select', 'test select', '', '<br />'], 5, 'Select')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<select name="test-select">\n<option value=""></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select_selected_not_present(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Select test-select \"test select\" \"\" \"<br />\""
      tokenized_lines = [(['Select', 'test-select', 'test select', '', '<br />'], 5, 'Select')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"test-select":"test-noun"}), mock_validation(), "", {})
      expected = '\n<select name="test-select">\n<option value="test-noun" selected class="temp">test-noun</option>\n<option value=""></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select_selected_not_present_2(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Select test-select \"test select\" \"\" \"<br />\""
      # . test-option "Test Option" "test option"
      tokenized_lines = [(['Select', 'test-select', 'test select', '', '<br />'], 5, 'Select'), (['.', 'test-option', 'Test Option', 'test option'], 4, '.')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"test-select":"test-noun"}), mock_validation(), "", {})
      expected = '\n<select name="test-select">\n<option value="test-option">Test Option</option>\n<option value="test-noun" selected class="temp">test-noun</option>\n<option value=""></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select_selected_present(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Select test-select \"test select\" \"\" \"<br />\""
      # . test-option "Test Option" "test option"
      tokenized_lines = [(['Select', 'test-select', 'test select', '', '<br />'], 5, 'Select'), (['.', 'test-option', 'Test Option', 'test option'], 4, '.')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"test-select":"test-option"}), mock_validation(), "", {})
      expected = '\n<select name="test-select">\n<option value="test-option" selected>Test Option</option>\n<option value=""></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select_ends(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Select supertypes "Noun type {i}" "Supertypes: " "<br />"
      # fillregex p=noun(?!{i}_)[0-9]+_name
      #
      # Label "Features:"
      tokenized_lines = [(['Select', 'supertypes', 'Noun type {i}', 'Supertypes: ', '<br />'], 5, 'Select'), (['fillregex', 'p=noun(?!{i}_)[0-9]+_name'], 2, 'fillregex'), (['Label', 'Features:'], 2, 'Label')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}, "test":{"name":"test-test"}}), mock_validation(), "", {})
      expected = 'Supertypes: \n<select name="supertypes" onfocus="fill(\'supertypes\', [].concat(fill_regex(\'noun(?!{i}_)[0-9]+_name\')));">\n<option value=""></option>\n</select><br />\nFeatures:\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_multiselect(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # MultiSelect test-multiselect "Test multiselect" "" "<br />"
      # fillverbpat
      tokenized_lines = [(['MultiSelect', 'test-multiselect', 'Test multiselect', '', '<br />'], 5, 'MultiSelect'), (['fillverbpat'], 1, 'fillverbpat')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<select name="test-multiselect" class="multi"  multiple="multiple"  onfocus="fill(\'test-multiselect\', [].concat(fill_case_patterns(false)));">\n<option value=""></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_multiselect_ends(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # MultiSelect supertypes "Noun type {i}" "Supertypes: " "<br />"
      # fillregex p=noun(?!{i}_)[0-9]+_name
      #
      # Label "Features:"
      tokenized_lines = [(['MultiSelect', 'supertypes', 'Noun type {i}', 'Supertypes: ', '<br />'], 5, 'MultiSelect'), (['fillregex', 'p=noun(?!{i}_)[0-9]+_name'], 2, 'fillregex'), (['Label', 'Features:'], 2, 'Label')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}, "test":{"name":"test-test"}}), mock_validation(), "", {})
      expected = 'Supertypes: \n<select name="supertypes" class="multi"  multiple="multiple"  onfocus="fill(\'supertypes\', [].concat(fill_regex(\'noun(?!{i}_)[0-9]+_name\')));">\n<option value=""></option>\n</select><br />\nFeatures:\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_text(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Text test \"Test name\" \"<p>Some test text: </p>\" \"<br />\" 42"
      tokenized_lines = [(['Text', 'test', 'Test name', '<p>Some test text: </p>', '<br />', '42'], 6, 'Text')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Some test text: </p><input type="text"  name="test" size="42"><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_textarea(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      #lines = ['TextArea test "Test name" "<p>A test text area:</p>" "<br />" 42x42']
      tokenized_lines = [(['TextArea', 'test', 'Test name', '<p>A test text area:</p>', '<br />', '42x42'], 6, 'TextArea')]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>A test text area:</p><TextArea name="test" cols="42" rows="42"></TextArea><br />\n'
      self.assertEqual(actual, expected)


  # defs_to_html with choices
  def testDefsToHtml_iter_example(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [(['BeginIter', 'test{i}', '"test-iter"'], 3, 'BeginIter'), (['Label', 'Test variable: {i}'], 2, 'Label'), (['EndIter', 'test'], 2, 'EndIter')]
      choices = load_choices("iter_choices.txt")
      actual = self._definition.defs_to_html(tokenized_lines, choices, mock_validation(), "", {})
      expected = """<div class="iterator" style="display: none" id="test_TEMPLATE">
<input type="button"  class="delbutton" title="Delete" value="X" onclick="remove_element('test{i}')">
<div class="iterframe">Test variable: {i}
</div>
</div>

<div class="iterator" id="test1">
<input type="button"  class="delbutton" title="Delete" value="X" onclick="remove_element('test1')">
<div class="iterframe">Test variable: 1
</div>
</div>
<div class="anchor" id="test_ANCHOR"></div>
<p><input type="button"  value="Add "test-iter"" onclick="clone_region('test', 'i', false)">"""
      self.assertEqual(actual, expected)


  def testDefsToHtml_iter_example2(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [(['BeginIter', 'test{i}', '"test-iter"'], 3, 'BeginIter'), (['Label', 'Test variable: {i}'], 2, 'Label'), (['EndIter', 'test'], 2, 'EndIter')]
      choices = load_choices("iter_choices2.txt")
      actual = self._definition.defs_to_html(tokenized_lines, choices, mock_validation(), "", {})
      expected = """<div class="iterator" style="display: none" id="test_TEMPLATE">
<input type="button"  class="delbutton" title="Delete" value="X" onclick="remove_element('test{i}')">
<div class="iterframe">Test variable: {i}
</div>
</div>

<div class="iterator" id="test1">
<input type="button"  class="delbutton" title="Delete" value="X" onclick="remove_element('test1')">
<div class="iterframe">Test variable: 1
</div>
</div>
<div class="iterator" id="test2">
<input type="button"  class="delbutton" title="Delete" value="X" onclick="remove_element('test2')">
<div class="iterframe">Test variable: 2
</div>
</div>
<div class="anchor" id="test_ANCHOR"></div>
<p><input type="button"  value="Add "test-iter"" onclick="clone_region('test', 'i', false)">"""
      self.assertEqual(actual, expected)


  def testDefsToHtml_select_example(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [(['Select', 'test-select', 'test select', '', '<br />'], 4, 'Select')]
      choices = load_choices("select_choices.txt")
      actual = self._definition.defs_to_html(tokenized_lines, choices, mock_validation(), "", {})
      expected = """\n<select name="test-select">
<option value="common" selected class="temp">common</option>
<option value=""></option>\n</select><br />\n"""
      self.assertEqual(actual, expected)


  def testDefsToHtml_section(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [(['Section', 'Test', 'test section', 'testSection'], 4, 'Section'), (['Label', 'test-label', 'test label'], 3, 'Label')]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({}), mock_validation(), "", {})
      expected = "test label\n"
      self.assertEqual(actual, expected)


class SubPageTests(unittest.TestCase):
  """
  TODO: Tests for conditional skipping
  TODO: Tests for striking options from select and multiselect
  TODO: Additional tests for validations errors
  TODO: Tests for section short name
  """

  def testBasic(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testBasic")
      actual = definition.sub_page('test-basic', '7777', mock_validation())
      expected = load_testhtml("testBasic")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testButton(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testButton")
      actual = definition.sub_page('test-button', '7777', mock_validation())
      expected = load_testhtml("testButton")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testCache(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testCache")
      actual = definition.sub_page('test-cache', '7777', mock_validation(), choices=mock_choices({"noun1":{"name":"test-noun"}, "verb1":{"name":"test-verb"}}))
      expected = load_testhtml("testCache")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testCheck(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testCheck")
      actual = definition.sub_page('test-check', '7777', mock_validation())
      expected = load_testhtml("testCheck")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testFile(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testFile")
      actual = definition.sub_page('test-file', '7777', mock_validation())
      expected = load_testhtml("testFile")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testHidden(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testHidden")
      actual = definition.sub_page('test-hidden', '7777', mock_validation())
      expected = load_testhtml("testHidden")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testIter(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testIter")
      actual = definition.sub_page('test-iter', '7777', mock_validation())
      expected = load_testhtml("testIter")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testNestedIter(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testNestedIter")
      actual = definition.sub_page('test-nested-iter', '7777', mock_validation())
      expected = load_testhtml("testNestedIter")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testIterBroken(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      self.assertRaises(MatrixDefSyntaxException, load_matrixdef("testIterBroken").sub_page, 'test-iter', '7777', mock_validation())


  def testSelect(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testSelect")
      actual = definition.sub_page('test-select', '7777', mock_validation())
      expected = load_testhtml("testSelect")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMultiSelect(self):
    """ TODO: Verify this test """
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testMultiSelect")
      actual = definition.sub_page('test-multiselect', '7777', mock_validation())
      expected = load_testhtml("testMultiSelect")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testRadios(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testRadios")
      actual = definition.sub_page('test-radios', '7777', mock_validation())
      expected = load_testhtml("testRadios")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testRadiosWithText(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testRadiosWithText")
      actual = definition.sub_page('test-radios-with-text', '7777', mock_validation())
      expected = load_testhtml("testRadiosWithText")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testText(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testText")
      actual = definition.sub_page('test-text', '7777', mock_validation())
      expected = load_testhtml("testText")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testTextArea(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testTextArea")
      actual = definition.sub_page('test-textarea', '7777', mock_validation())
      expected = load_testhtml("testTextArea")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testJoinedLines(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testJoinedLines")
      actual = definition.sub_page('test-joined-lines', '7777', mock_validation())
      expected = load_testhtml("testJoinedLines")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMultipleSections(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testMultipleSections")
      actual1 = definition.sub_page('test-basic', '7777', mock_validation())
      actual2 = definition.sub_page('test-basic-2', '7777', mock_validation())
      expected1 = load_testhtml("testMultipleSections1")
      expected2 = load_testhtml("testMultipleSections2")
      self.assertEqual(remove_empty_lines(actual1), remove_empty_lines(expected1))
      self.assertEqual(remove_empty_lines(actual2), remove_empty_lines(expected2))



class MainPageTests(unittest.TestCase):
  """
  TODO: Need to write tests for displaying choices
  TODO: Need to write tests for displaying validation messages
  """

  def testMainPage_basic(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testBasic")
      actual = definition.main_page('7777', mock_validation())
      expected = load_testhtml("testMainPage")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMainPage_error(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load_matrixdef("testBasic")
      actual = definition.main_page('7777', mock_validation(errors={"test-basic":mock_error(message="error")}))
      expected = load_testhtml("testMainPageError")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMainPage_simple_choices(self):
    # TODO: This test should be simplified, either by improving the test or improving main_page()
    with os_environ(HTTP_COOKIE="session=7777"), choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      definition = load_matrixdef("testMinimalLexiconMorphology")
      shutil.copyfile(env.choices_file.name, 'sessions/7777/choices')
      actual = definition.main_page('7777', mock_validation())
      os.remove('sessions/7777/choices')
      expected = load_testhtml("testMainPageMinimalLexiconMorphology")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMainPage_lexicon_choices(self):
    # TODO: This test should be simplified, either by improving the test or improving main_page()
    with os_environ(HTTP_COOKIE="session=7777"), choice_environ('lexicon', 'lexicon_choices2.txt') as env:
      definition = load_matrixdef("testMinimalLexiconMorphology")
      shutil.copyfile(env.choices_file.name, 'sessions/7777/choices')
      actual = definition.main_page('7777', mock_validation())
      os.remove('sessions/7777/choices')
      expected = load_testhtml("testMainPageFullChoices")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


class NavigationTests(unittest.TestCase):

  def testNavigation_Basic(self):
    definition = load_matrixdef("testBasic")
    actual = definition.navigation(mock_validation(), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a data-name="Test Basic" class="navlinks" href="#" onclick="submit_go('test-basic')">Test Basic</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize('tgz')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize('zip')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_MultipleSections(self):
    definition = load_matrixdef("testMultipleSections")
    actual = definition.navigation(mock_validation(), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a data-name="Test Basic" class="navlinks" href="#" onclick="submit_go('test-basic')">Test Basic</a><br />
<span style="color:#ff0000;" class="navleft"></span><a data-name="Test Basic 2" class="navlinks" href="#" onclick="submit_go('test-basic-2')">Test Basic 2</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize('tgz')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize('zip')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_HiddenSection(self):
    definition = load_matrixdef("testHiddenSection")
    actual = definition.navigation(mock_validation(), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a data-name="Test Section" class="navlinks" href="#" onclick="submit_go('test-section')">Test Section</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize('tgz')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize('zip')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_Errors(self):
    definition = load_matrixdef("testRadios")
    actual = definition.navigation(mock_validation(errors={"test-radio":mock_error(message="error")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft">*</span><a data-name="Test Radios" class="navlinks" href="#" onclick="submit_go('test-radios')">Test Radios</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:
<a href="" style="text-decoration:none"><span class="info" title="Resolve validation errors to enable grammar customization.">#</span></a>
</span><br />
<span class="navleft" style="padding-left:15px">tgz</span>, <span class="navleft">zip</span>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_ShortName(self):
    definition = load_matrixdef("testShortName")
    actual = definition.navigation(mock_validation(errors={"test-radio":mock_error(message="error")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a data-name="Test Basic" data-short-name="basic" class="navlinks" href="#" onclick="submit_go('test-basic')">Test Basic</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:
<a href="" style="text-decoration:none"><span class="info" title="Resolve validation errors to enable grammar customization.">#</span></a>
</span><br />
<span class="navleft" style="padding-left:15px">tgz</span>, <span class="navleft">zip</span>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_RadiosWarnings(self):
    definition = load_matrixdef("testRadios")
    actual = definition.navigation(mock_validation(warnings={"test-radio":mock_error(message="warning")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft">?</span><a data-name="Test Radios" class="navlinks" href="#" onclick="submit_go('test-radios')">Test Radios</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize('tgz')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize('zip')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_NestedIterErrors(self):
    definition = load_matrixdef("testNestedIter")
    actual = definition.navigation(mock_validation(errors={"test-nested1_test-nested-inner1_name":mock_error(message="errors")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft">*</span><a data-name="Test Nested Iter" class="navlinks" href="#" onclick="submit_go('test-nested-iter')">Test Nested Iter</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:
<a href="" style="text-decoration:none"><span class="info" title="Resolve validation errors to enable grammar customization.">#</span></a>
</span><br />
<span class="navleft" style="padding-left:15px">tgz</span>, <span class="navleft">zip</span>
</div>"""
    self.assertEqual(actual, expected)


class GetOnLoadTests(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls._definition = deffile.MatrixDef(None)

  def testBasic_Onload(self):
    actual = self._definition.get_onload([([u'Section', u'test-basic', u'Test Basic', u'TestBasic', u'testBasic', u'unload();'], 6, u'Section')])
    expected = u'unload();'
    self.assertEqual(actual, expected)

  def testBasic_None(self):
    actual = self._definition.get_onload([([u'Section', u'test-basic', u'Test Basic', u'TestBasic', u'testBasic'], 5, u'Section')])
    expected = u''
    self.assertEqual(actual, expected)


class ReplaceVarsTests(unittest.TestCase):

  def testReplaceVars_Multiple(self):
    actual = deffile.replace_vars("BeginIter test-iter-{i} \"hello\" \"\"", {"i":1})
    expected = "BeginIter test-iter-1 \"hello\" \"\""
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized(self):
    actual = deffile.replace_vars_tokenized((['BeginIter', 'test-iter-{i}', '"hello"', ''], 4, 'BeginIter'), {"i":1})
    expected = (['BeginIter', 'test-iter-1', '"hello"', ''], 4, 'BeginIter')
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_non1(self):
    actual = deffile.replace_vars_tokenized((['BeginIter', 'test-iter-{i}', '"hello"', ''], 4, 'BeginIter'), {"i":2})
    expected = (['BeginIter', 'test-iter-2', '"hello"', ''], 4, 'BeginIter')
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_Multiple(self):
    actual = deffile.replace_vars_tokenized((['BeginIter', 'test-iter-{i}-{j}', '"hello"', ''], 4, 'BeginIter'), {"i":1, "j":2})
    expected = (['BeginIter', 'test-iter-1-2', '"hello"', ''], 4, 'BeginIter')
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_NoMutation(self):
    line = (['BeginIter', 'test-iter-{i}', '"hello"', ''], 4, 'BeginIter')
    line_copy = (['BeginIter', 'test-iter-{i}', '"hello"', ''], 4, 'BeginIter')
    actual = deffile.replace_vars_tokenized(line, {"i":1})
    expected = (['BeginIter', 'test-iter-1', '"hello"', ''], 4, 'BeginIter')
    self.assertEqual(line, line_copy)
    self.assertEqual(actual, expected)
    actual = deffile.replace_vars_tokenized(line, {"i":2})
    expected = (['BeginIter', 'test-iter-2', '"hello"', ''], 4, 'BeginIter')
    self.assertEqual(line, line_copy)
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_Missing(self):
    actual = deffile.replace_vars_tokenized((['BeginIter', 'test-iter-{i}-{j}', '"hello"', ''], 4, 'BeginIter'), {"i":1, "k":2})
    expected = (['BeginIter', 'test-iter-1-{j}', '"hello"', ''], 4, 'BeginIter')
    self.assertEqual(actual, expected)


class SaveChoicesTests(unittest.TestCase):
  """
  TODO: Tests for nested iters
  TODO: Tests for choice adding functions
  NOTE: Using named temp file because save_choices expects a path
  """

  @classmethod
  def setUpClass(cls):
    cls._definition = deffile.MatrixDef(os.path.join("gmcs", "tests", "resources", "test_defs", "testMinimalLexiconMorphology"))


  # Generic tests
  def testSaveChoicesSection_noChanges_currentPage(self):
    with choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      env.choices_file.seek(0)
      expected = env.choices_file.read()
      env.form_data['noun1_name'] = FormInfo('noun1_name', 'common')
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_noChanges_otherPage(self):
    with choice_environ('morphology', 'min_lexicon_morphology.txt') as env:
      env.choices_file.seek(0)
      expected = env.choices_file.read()
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_currentPage_add(self):
    with choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      env.form_data['noun1_name'] = FormInfo('noun1_name', 'common')
      env.form_data['noun1_det'] = FormInfo('noun1_det', 'obl')
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = "\nversion=28\n\nsection=lexicon\n  noun1_name=common\n  noun1_det=obl\n\nsection=morphology\n"
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_currentPage_remove(self):
    with choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = "\nversion=28\n\nsection=lexicon\n\nsection=morphology\n"
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_otherPage_noChanges(self):
    with choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      env.form_data['noun1_name'] = FormInfo('noun1_name', 'common')
      env.form_data['noun-pc1_name'] = FormInfo('noun-pc1_name', "test")
      env.form_data['noun-pc1_obligatory'] = FormInfo('noun-pc1_obligatory', "on")
      env.form_data['noun-pc1_order'] = FormInfo('noun-pc1_order', "suffix")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = "\nversion=28\n\nsection=lexicon\n  noun1_name=common\n\nsection=morphology\n"
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_multipleChoices(self):
    with choice_environ('morphology', 'min_lexicon_morphology.txt') as env:
      env.form_data['noun-pc1_name'] = FormInfo('noun-pc1_name', "test")
      env.form_data['noun-pc1_obligatory'] = FormInfo('noun-pc1_obligatory', "on")
      env.form_data['noun-pc1_order'] = FormInfo('noun-pc1_order', "suffix")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = "\nversion=28\n\nsection=lexicon\n  noun1_name=common\n\nsection=morphology\n  noun-pc1_name=test\n  noun-pc1_obligatory=on\n  noun-pc1_order=suffix\n"
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  # Choice adding method tests
  def testSaveChoicesSection_optionallyCopulaComplement_new(self):
    with choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      env.form_data['adj1_name'] = FormInfo('adj1_name', "test")
      env.form_data['adj1_predcop'] = FormInfo('adj1_predcop', "opt")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = load_file(os.path.join(*(env.path + ['optionally_copula_complement_after.txt'])))
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_optionallyCopulaComplement_other_page(self):
    with choice_environ('general', 'min_lexicon_morphology.txt') as env:
      # Wrong page, do nothing # TODO: Confirm this
      env.form_data['adj1_name'] = FormInfo('adj1_name', "test")
      env.form_data['adj1_predcop'] = FormInfo('adj1_predcop', "opt")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = load_file(os.path.join(*(env.path + ['min_lexicon_morphology.txt'])))
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_optionallyCopulaComplement_existing(self):
    with choice_environ('lexicon', 'optionally_copula_complement_after.txt') as env:
      env.form_data['adj1_name'] = FormInfo('adj1_name', "test")
      env.form_data['adj1_predcop'] = FormInfo('adj1_predcop', "opt")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = load_file(os.path.join(*(env.path + ['optionally_copula_complement_after.txt'])))
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_lexicon_add_adj_arg_agreement_feats(self):
    with choice_environ('lexicon', 'min_lexicon_morphology.txt') as env:
      env.form_data['adj1_name'] = FormInfo('adj1_name', "test")
      env.form_data['adj1_predcop'] = FormInfo('adj1_predcop', "obl")
      env.form_data['adj1_feat1_name'] = FormInfo('adj1_feat1_name', "person")
      env.form_data['adj1_feat1_value'] = FormInfo('adj1_feat1_value', "3rd")
      env.form_data['adj1_feat1_head'] = FormInfo('adj1_feat1_head', "subj")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = load_file(os.path.join(*(env.path + ['adj_arg_agreement_lex_after.txt'])))
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testSaveChoicesSection_morphology_add_adj_arg_agreement_feats(self):
    with choice_environ('morphology', 'min_lexicon_morphology.txt') as env:
      env.form_data['adj-pc1_name'] = FormInfo('adj-pc1_name', "test_pc")
      env.form_data['adj-pc1_lrt1_name'] = FormInfo('adj-pc1_lrt1_name', "test_lrt")
      env.form_data['adj-pc1_lrt1_feat1_name'] = FormInfo('adj-pc1_lrt1_feat1_name', "person")
      env.form_data['adj-pc1_lrt1_feat1_value'] = FormInfo('adj-pc1_lrt1_feat1_value', "3rd")
      env.form_data['adj-pc1_lrt1_feat1_head'] = FormInfo('adj-pc1_lrt1_feat1_head', "subj")
      self._definition.save_choices(env.form_data, env.choices_file.name)
      env.choices_file.seek(0)
      actual = env.choices_file.read()
      expected = load_file(os.path.join(*(env.path + ['adj_arg_agreement_morph_after.txt'])))
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


class SaveChoicesSectionTests(unittest.TestCase):
  """
  NOTE: Using StringIO because it's simpler and save_choices_section expects a file object
  """

  @classmethod
  def setUpClass(cls):
    cls._definition = deffile.MatrixDef(None)


  def testSaveChoicesSection_basic(self):
    io = StringIO.StringIO()
    tokenized_lines = [(['Check', 'test-check', 'test-check', 'check: ', ''], 5, 'Check')]
    self._definition.save_choices_section(tokenized_lines, io, mock_choices({"test-check":"on"}))
    actual = io.getvalue()
    expected = "test-check=on\n"
    self.assertEqual(actual, expected)


  def testSaveChoicesSection_basic2(self):
    io = StringIO.StringIO()
    tokenized_lines = [(['Check', 'test-check', 'test-check', 'check: ', ''], 5, 'Check')]
    self._definition.save_choices_section(tokenized_lines, io, mock_choices({"test-check":"off"}))
    actual = io.getvalue()
    expected = "test-check=off\n"
    self.assertEqual(actual, expected)


  def testSaveChoicesSection_iter(self):
    io = StringIO.StringIO()
    choices = load_choices("iter_choices.txt")
    tokenized_lines = [(['BeginIter', 'test{i}', '"test-iter"'], 3, 'BeginIter'), (['Text', 'name', 'Test variable: {i}', "", "", "20"], 6, 'Text'), (['EndIter', 'test'], 2, 'EndIter')]
    self._definition.save_choices_section(tokenized_lines, io, choices)
    actual = io.getvalue()
    expected = "  test1_name=common\n"
    self.assertEqual(actual, expected)


  def testSaveChoicesSection_iter(self):
    io = StringIO.StringIO()
    choices = load_choices("iter_check_choices.txt")
    tokenized_lines = [(['Check', 'test-check', 'test-check', 'check: ', ''], 5, 'Check'), (['BeginIter', 'test{i}', '"test-iter"'], 3, 'BeginIter'), (['Text', 'name', 'Test variable: {i}', "", "", "20"], 6, 'Text'), (['EndIter', 'test'], 2, 'EndIter')]
    self._definition.save_choices_section(tokenized_lines, io, choices)
    actual = io.getvalue()
    expected = "test-check=on\n  test1_name=common\n"
    self.assertEqual(actual, expected)


  def testSaveChoicesSection_nestedIter(self):
    io = StringIO.StringIO()
    choices = load_choices("iter_nested_check_choices.txt")
    tokenized_lines = [(['Check', 'test-check', 'test-check', 'check: ', ''], 5, 'Check'), (['BeginIter', 'test{i}', '"test-iter"'], 3, 'BeginIter'), (['Text', 'name', 'Test variable: {i}', "", "", "20"], 6, 'Text'), (['BeginIter', 'test-nested{j}', '"test-iter"'], 3, 'BeginIter'), (['Text', 'name', 'Test variable: {i} {j}', "", "", "20"], 6, 'Text'), (['EndIter', 'test-nested'], 2, 'EndIter'), (['EndIter', 'test'], 2, 'EndIter')]
    self._definition.save_choices_section(tokenized_lines, io, choices)
    actual = io.getvalue()
    expected = "test-check=on\n  test1_name=test-name\n    test1_test-nested1_name=common\n"
    self.assertEqual(actual, expected)
