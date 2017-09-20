import unittest

import os
import re

from gmcs import html
from gmcs import deffile
from gmcs.choices import ChoicesFile
from gmcs.deffile import MatrixDefSyntaxException

from mock import mock_choices, mock_validation, mock_error, os_environ


def get_path(*path):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))


def load(file_name):
  path = get_path("resources", "test_defs", file_name)
  return deffile.MatrixDef(path)


def load_expected(file_name):
  path = get_path("resources", "test_html", file_name + ".html")
  with open(path, 'r') as f:
    return f.read()


def remove_empty_lines(string):
  return "\n".join((line.strip() for line in string.split("\n") if line.strip()))


def print_both(actual, expected):
  print("#"*50 + " ACTUAL " + "#"*50)
  print(actual)
  print
  print("#"*50 + " EXPECTED " + "#"*50)
  print(expected)


### TESTS
class InitializerTests(unittest.TestCase):

  def testInitializer_Basic(self):
    definition = load("testBasic")

    self.assertEqual(definition.tokenized_lines, [['Section', 'test-basic', 'Test Basic', 'TestBasic'], ['Label', '<p>Test</p>'], ['Separator'], ['Label', '<p>Test</p>']])
    self.assertEqual(definition.sections, {'test-basic': [['Section', 'test-basic', 'Test Basic', 'TestBasic'], ['Label', '<p>Test</p>'], ['Separator'], ['Label', '<p>Test</p>']]})
    self.assertEqual(definition.section_names, {'test-basic':'Test Basic'})
    self.assertEqual(definition.doc_links, {'test-basic':'TestBasic'})


  def testInitializer_MultipleSections(self):
    definition = load("testMultipleSections")

    self.assertEqual(definition.tokenized_lines, [['Section', 'test-basic', 'Test Basic', 'TestBasic'], ['Label', '<p>Test</p>'], ['Section', 'test-basic-2', 'Test Basic 2', 'TestBasic2'], ['Label', '<p>Test2</p>']])
    self.assertEqual(definition.sections, {'test-basic': [['Section', 'test-basic', 'Test Basic', 'TestBasic'], ['Label', '<p>Test</p>']], 'test-basic-2': [['Section', 'test-basic-2', 'Test Basic 2', 'TestBasic2'], ['Label', '<p>Test2</p>']]})
    self.assertEqual(definition.section_names, {'test-basic': 'Test Basic', 'test-basic-2': 'Test Basic 2'})
    self.assertEqual(definition.doc_links, {'test-basic': 'TestBasic', 'test-basic-2': 'TestBasic2'})


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
      tokenized_lines = [['Cache', 'nouns', 'noun[0-9]+$', 'name']]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}}), mock_validation(), "", {})
      expected = '<script type="text/javascript">\n// A cache of choices from other subpages\nvar nouns = [\n\'test-noun:noun1\',\n];\n</script>'
      self.assertEqual(actual, expected)


  @unittest.skip("Need to figure out how choices object is structured and enhance mock_choices object")
  def testDefsToHtml_iter(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [['BeginIter', 'test{i}', '"test-iter"'], ['Text', 'name', 'Test variable: {i}', "", "", "20"], ['EndIter', 'test']]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}, "test":{"name":"test-test"}}), mock_validation(), "", {})
      expected = ''
      self.assertEqual(actual, expected)


  @unittest.skip("Need to figure out how choices object is structured and enhance mock_choices object")
  def testDefsToHtml_iter_cookie(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      tokenized_lines = [['BeginIter', 'test{i}', '"test-iter"'], ['Text', 'name', 'Test variable: {i}', "", "", "20"], ['EndIter', 'test']]
      actual = self._definition.defs_to_html(tokenized_lines, mock_choices({"noun1":{"name":"test-noun"}, "test":{"name":"test-test"}}), mock_validation(), "", {})
      expected = ''
      self.assertEqual(actual, expected)


  def testDefsToHtml_label(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Label "<p>Test</p>"
      tokenized_lines = [['Label', '<p>Test</p>']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Test</p>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_separator(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Separator
      tokenized_lines = [['Separator']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<hr>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_button(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Button test-button "<p>Test Button: " "</p>" ""
      tokenized_lines = [['Button', 'test-button', '<p>Test Button: ', '</p>', '']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Test Button: <input type="button"  value="test-button"></p>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_check(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Check test-check "test-check" "check: " "" "testMe();"
      tokenized_lines = [['Check', 'test-check', 'test-check', 'check: ', '', 'testMe();']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<label>check: <input type="checkbox"  name="test-check" onclick="testMe();"></label>\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_file(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # File test-file "test file" "<p>Test file: </p>" ""
      tokenized_lines = [['File', 'test-file', 'test file', '<p>Test file: </p>', '']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Test file: </p><input type="file"  name="test-file">\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_hidden(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # Hidden test-hidden "test hidden"
      tokenized_lines = [['Hidden', 'test-hidden', 'test hidden']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<input type="hidden"  name="test-hidden">\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_radio(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Radio test-radio \"test radio\" \"\" \"\"", ". test-bullet1 \"hello\" \"\" \"\" \"\"", ". test-bullet2 \"world\" \"\" \"\" \"\""
      tokenized_lines = [['Radio', 'test-radio', 'test radio', '', ''], ['.', 'test-bullet1', 'hello', '', '', ''], ['.', 'test-bullet2', 'world', '', '', '']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<label><input type="radio"  name="test-radio" value="test-bullet1"></label>\n<label><input type="radio"  name="test-radio" value="test-bullet2"></label>\n\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Select test-select \"test select\" \"\" \"<br />\""
      tokenized_lines = [['Select', 'test-select', 'test select', '', '<br />']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<select name="test-select">\n<option value="" selected class="temp"></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_multiselect(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # MultiSelect test-multiselect "Test multiselect" "" "<br />"
      # fillverbpat
      tokenized_lines = [['MultiSelect', 'test-multiselect', 'Test multiselect', '', '<br />'], ['fillverbpat']]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<select name="test-multiselect" class="multi"  multiple="multiple"  onfocus="fill(\'test-multiselect\', [].concat(fill_case_patterns(false)));">\n<option value="" selected class="temp"></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_text(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Text test \"Test name\" \"<p>Some test text: </p>\" \"<br />\" 42"
      tokenized_lines = [["Text", "test", "Test name", "<p>Some test text: </p>", "<br />", "42"]]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Some test text: </p><input type="text"  name="test" size="42"><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_textarea(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      #lines = ['TextArea test "Test name" "<p>A test text area:</p>" "<br />" 42x42']
      tokenized_lines = [["TextArea", "test", "Test name", "<p>A test text area:</p>", "<br />", "42x42"]]
      actual = self._definition.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>A test text area:</p><TextArea name="test" cols="42" rows="42"></TextArea><br />\n'
      self.assertEqual(actual, expected)


class SubPageTests(unittest.TestCase):
  """
  TODO: Tests for conditional skipping
  TODO: Tests for striking options from select and multiselect
  TODO: Additional tests for validations errors
  """

  def testBasic(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testBasic")
      actual = definition.sub_page('test-basic', '7777', mock_validation())
      expected = load_expected("testBasic")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testButton(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testButton")
      actual = definition.sub_page('test-button', '7777', mock_validation())
      expected = load_expected("testButton")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testCache(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testCache")
      actual = definition.sub_page('test-cache', '7777', mock_validation(), choices=mock_choices({"noun1":{"name":"test-noun"}, "verb1":{"name":"test-verb"}}))
      expected = load_expected("testCache")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testCheck(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testCheck")
      actual = definition.sub_page('test-check', '7777', mock_validation())
      expected = load_expected("testCheck")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testFile(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testFile")
      actual = definition.sub_page('test-file', '7777', mock_validation())
      expected = load_expected("testFile")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testHidden(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testHidden")
      actual = definition.sub_page('test-hidden', '7777', mock_validation())
      expected = load_expected("testHidden")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testIter(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testIter")
      actual = definition.sub_page('test-iter', '7777', mock_validation())
      expected = load_expected("testIter")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testNestedIter(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testNestedIter")
      actual = definition.sub_page('test-nested-iter', '7777', mock_validation())
      expected = load_expected("testNestedIter")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testIterBroken(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      self.assertRaises(MatrixDefSyntaxException, load("testIterBroken").sub_page, 'test-iter', '7777', mock_validation())


  def testSelect(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testSelect")
      actual = definition.sub_page('test-select', '7777', mock_validation())
      expected = load_expected("testSelect")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMultiSelect(self):
    """ TODO: Verify this test """
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testMultiSelect")
      actual = definition.sub_page('test-multiselect', '7777', mock_validation())
      expected = load_expected("testMultiSelect")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testRadios(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testRadios")
      actual = definition.sub_page('test-radios', '7777', mock_validation())
      expected = load_expected("testRadios")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testRadiosWithText(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testRadiosWithText")
      actual = definition.sub_page('test-radios-with-text', '7777', mock_validation())
      expected = load_expected("testRadiosWithText")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testText(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testText")
      actual = definition.sub_page('test-text', '7777', mock_validation())
      expected = load_expected("testText")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testTextArea(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testTextArea")
      actual = definition.sub_page('test-textarea', '7777', mock_validation())
      expected = load_expected("testTextArea")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testJoinedLines(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testJoinedLines")
      actual = definition.sub_page('test-joined-lines', '7777', mock_validation())
      expected = load_expected("testJoinedLines")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMultipleSections(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testMultipleSections")
      actual1 = definition.sub_page('test-basic', '7777', mock_validation())
      actual2 = definition.sub_page('test-basic-2', '7777', mock_validation())
      expected1 = load_expected("testMultipleSections1")
      expected2 = load_expected("testMultipleSections2")
      self.assertEqual(remove_empty_lines(actual1), remove_empty_lines(expected1))
      self.assertEqual(remove_empty_lines(actual2), remove_empty_lines(expected2))


class MainPageTests(unittest.TestCase):
  """
  TODO: Need to write tests for displaying choices
  TODO: Need to write tests for displaying validation messages
  """

  def testMainPage_basic(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testBasic")
      actual = definition.main_page('7777', mock_validation())
      expected = load_expected("testMainPage")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


  def testMainPage_error(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testBasic")
      actual = definition.main_page('7777', mock_validation(errors={"test-basic":mock_error(message="error")}))
      expected = load_expected("testMainPageError")
      self.assertEqual(remove_empty_lines(actual), remove_empty_lines(expected))


class NavigationTests(unittest.TestCase):

  def testNavigation_Basic(self):
    definition = load("testBasic")
    actual = definition.navigation(mock_validation(), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a class="navlinks" href="#" onclick="submit_go('test-basic')">Test Basic</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize('tgz')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize('zip')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_MultipleSections(self):
    definition = load("testMultipleSections")
    actual = definition.navigation(mock_validation(), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a class="navlinks" href="#" onclick="submit_go(\'test-basic\')">Test Basic</a><br />
<span style="color:#ff0000;" class="navleft"></span><a class="navlinks" href="#" onclick="submit_go(\'test-basic-2\')">Test Basic 2</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize(\'tgz\')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize(\'zip\')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_Errors(self):
    definition = load("testRadios")
    actual = definition.navigation(mock_validation(errors={"test-radio":mock_error(message="error")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft">*</span><a class="navlinks" href="#" onclick="submit_go('test-radios')">Test Radios</a><br />
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
    definition = load("testRadios")
    actual = definition.navigation(mock_validation(warnings={"test-radio":mock_error(message="warning")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft">?</span><a class="navlinks" href="#" onclick="submit_go('test-radios')">Test Radios</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize('tgz')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize('zip')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_NestedIterErrors(self):
    definition = load("testNestedIter")
    actual = definition.navigation(mock_validation(errors={"test-nested1_test-nested-inner1_name":mock_error(message="errors")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft">*</span><a class="navlinks" href="#" onclick="submit_go('test-nested-iter')">Test Nested Iter</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:
<a href="" style="text-decoration:none"><span class="info" title="Resolve validation errors to enable grammar customization.">#</span></a>
</span><br />
<span class="navleft" style="padding-left:15px">tgz</span>, <span class="navleft">zip</span>
</div>"""
    self.assertEqual(actual, expected)


class ReplaceVarsTests(unittest.TestCase):


  def testReplaceVars_Multiple(self):
    actual = deffile.replace_vars("BeginIter test-iter-{i} \"hello\" \"\"", {"i":1})
    expected = "BeginIter test-iter-1 \"hello\" \"\""
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized(self):
    actual = deffile.replace_vars_tokenized(["BeginIter", "test-iter-{i}", '"hello"', ""], {"i":1})
    expected = ["BeginIter", "test-iter-1", '"hello"', ""]
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_non1(self):
    actual = deffile.replace_vars_tokenized(["BeginIter", "test-iter-{i}", '"hello"', ""], {"i":2})
    expected = ["BeginIter", "test-iter-2", '"hello"', ""]
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_Multiple(self):
    actual = deffile.replace_vars_tokenized(["BeginIter", "test-iter-{i}-{j}", '"hello"', ""], {"i":1, "j":2})
    expected = ["BeginIter", "test-iter-1-2", '"hello"', ""]
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_Missing(self):
    actual = deffile.replace_vars_tokenized(["BeginIter", "test-iter-{i}-{j}", '"hello"', ""], {"i":1, "k":2})
    expected = ["BeginIter", "test-iter-1-{j}", '"hello"', ""]
    self.assertEqual(actual, expected)
