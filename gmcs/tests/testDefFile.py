import unittest

import os

from gmcs import deffile
from gmcs.choices import ChoicesFile


def get_path(*path):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

def load(file_name):
  path = get_path("resources", "test_defs", file_name)
  return deffile.MatrixDefFile(path)

def load_expected(file_name):
  path = get_path("resources", "test_html", file_name + ".html")
  with open(path, 'r') as f:
    return f.read()

def remove_empty_lines(string):
  return "\n".join((line for line in string.split("\n") if line.strip()))


def __print_both(actual, expected):
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
  """

  @classmethod
  def setUpClass(cls):
    DefsToHtmlTests.__def = load("testBasic")


  def testDefsToHtml_radio(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Radio test-radio \"test radio\" \"\" \"\"", ". test-bullet1 \"hello\" \"\" \"\" \"\"", ". test-bullet2 \"world\" \"\" \"\" \"\""
      tokenized_lines = [['Radio', 'test-radio', 'test radio', '', ''], ['.', 'test-bullet1', 'hello', '', '', ''], ['.', 'test-bullet2', 'world', '', '', '']]
      actual = DefsToHtmlTests.__def.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<label><input type="radio"  name="test-radio" value="test-bullet1"></label>\n<label><input type="radio"  name="test-radio" value="test-bullet2"></label>\n\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_select(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Select test-select \"test select\" \"\" \"<br />\""
      tokenized_lines = [['Select', 'test-select', 'test select', '', '<br />']]
      actual = DefsToHtmlTests.__def.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '\n<select name="test-select">\n<option value="" selected class="temp"></option>\n</select><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_text(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      # "Text test \"Test name\" \"<p>Some test text: </p>\" \"<br />\" 42"
      tokenized_lines = [["Text", "test", "Test name", "<p>Some test text: </p>", "<br />", "42"]]
      actual = DefsToHtmlTests.__def.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>Some test text: </p><input type="text"  name="test" size="42"><br />\n'
      self.assertEqual(actual, expected)


  def testDefsToHtml_textarea(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      #lines = ['TextArea test "Test name" "<p>A test text area:</p>" "<br />" 42x42']
      tokenized_lines = [["TextArea", "test", "Test name", "<p>A test text area:</p>", "<br />", "42x42"]]
      actual = DefsToHtmlTests.__def.defs_to_html(tokenized_lines, {}, mock_validation(), "", {})
      expected = '<p>A test text area:</p><TextArea name="test" cols="42" rows="42"></TextArea><br />\n'
      self.assertEqual(actual, expected)


class SubPageTests(unittest.TestCase):
  """
  TODO: Tests for conditional skipping
  TODO: Tests for striking options from select and multiselect
  """

  def __print_both(self, actual, expected):
    print("#"*50 + " ACTUAL " + "#"*50)
    print(actual)
    print
    print("#"*50 + " EXPECTED " + "#"*50)
    print(expected)


  def testBasic(self):
    with os_environ(HTTP_COOKIE="session=7777"):
      definition = load("testBasic")
      actual = definition.sub_page('test-basic', '7777', mock_validation())
      expected = load_expected("testBasic")
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
      self.assertRaises(Exception, load("testIterBroken"))


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


  def testNavigation_Warnings(self):
    definition = load("testBasic")
    actual = definition.navigation(mock_validation(warnings={"test-basic":mock_error(message="warning")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a class="navlinks" href="#" onclick="submit_go(\'test-basic\')">Test Basic</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:</span><br />
<a href="#" onclick="nav_customize(\'tgz\')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize(\'zip\')" class="navleft">zip</a>
</div>"""
    self.assertEqual(actual, expected)


  def testNavigation_Errors(self):
    definition = load("testBasic")
    actual = definition.navigation(mock_validation(errors={"test-basic":mock_error(message="errror")}), "dummy_choices")
    expected = """<div id="navmenu"><br />
<a href="." onclick="submit_main()" class="navleft">Main page</a><br />
<hr />
<span style="color:#ff0000;" class="navleft"></span><a class="navlinks" href="#" onclick="submit_go(\'test-basic\')">Test Basic</a><br />
<hr />
<a href="dummy_choices" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>
<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />
<span class="navleft">Create grammar:
<a href="" style="text-decoration:none"><span class="info" title="Resolve validation errors to enable grammar customization.">#</span></a>
</span><br />
<span class="navleft" style="padding-left:15px">tgz</span>, <span class="navleft">zip</span>"""
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


class HtmlSelectTests(unittest.TestCase):

  def testHtmlSelect_basic(self):
    actual = deffile.html_select(mock_validation(), "hello")
    expected = '<select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_onfocus(self):
    actual = deffile.html_select(mock_validation(), "hello", onfocus="test();")
    expected = '<select name="hello" onfocus="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_onchange(self):
    actual = deffile.html_select(mock_validation(), "hello", onchange="test();")
    expected = '<select name="hello" onchange="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_onfocus_onchange(self):
    actual = deffile.html_select(mock_validation(), "hello", onfocus="test1();", onchange="test2();")
    expected = '<select name="hello" onfocus="test1();" onchange="test2();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_warning(self):
    actual = deffile.html_select(mock_validation(warnings={"hello":mock_error(message="warning")}), "hello")
    expected = '<a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_error(self):
    actual = deffile.html_select(mock_validation(errors={"hello":mock_error(message="error")}), "hello")
    expected = '<a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_info(self):
    actual = deffile.html_select(mock_validation(infos={"hello":mock_error(message="info")}), "hello")
    expected = '<a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_basic(self):
    actual = deffile.html_select(mock_validation(), "hello", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_onfocus(self):
    actual = deffile.html_select(mock_validation(), "hello", onfocus="test();", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple"  onfocus="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_onchange(self):
    actual = deffile.html_select(mock_validation(), "hello", onchange="test();", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple"  onchange="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_onfocus_onchange(self):
    actual = deffile.html_select(mock_validation(), "hello", onfocus="test1();", onchange="test2();", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple"  onfocus="test1();" onchange="test2();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_warning(self):
    actual = deffile.html_select(mock_validation(warnings={"hello":mock_error(message="warning")}), "hello", multi=True)
    expected = '<a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_error(self):
    actual = deffile.html_select(mock_validation(errors={"hello":mock_error(message="error")}), "hello", multi=True)
    expected = '<a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_info(self):
    actual = deffile.html_select(mock_validation(infos={"hello":mock_error(message="info")}), "hello", multi=True)
    expected = '<a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


class HtmlInputTests(unittest.TestCase):
  """
  Input types:
  check, radio, text, textarea, file, button, submit, hidden
  """

  def testHtmlInput_radio_basic(self):
    actual = deffile.html_input(mock_validation(), "radio", "hello", "test_value", False)
    expected = '<label><input type="radio"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_disabled(self):
    actual = deffile.html_input(mock_validation(), "radio", "hello", "test_value", False, disabled=True)
    expected = '<label><input type="radio"  name="hello" value="test_value" disabled="disabled"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_onclick(self):
    actual = deffile.html_input(mock_validation(), "radio", "hello", "test_value", False, onclick="helloworld();")
    expected = '<label><input type="radio"  name="hello" value="test_value" onclick="helloworld();"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_before(self):
    actual = deffile.html_input(mock_validation(), "radio", "hello", "test_value", False, before="Button: ")
    expected = '<label>Button: <input type="radio"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_after(self):
    actual = deffile.html_input(mock_validation(), "radio", "hello", "test_value", False, after="</div>")
    expected = '<label><input type="radio"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_before_after(self):
    actual = deffile.html_input(mock_validation(), "radio", "hello", "test_value", False, before="<div>Button: ", after="</div>")
    expected = '<label><div>Button: <input type="radio"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_basic(self):
    actual = deffile.html_input(mock_validation(), "checkbox", "hello", "test_value", False)
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_disabled(self):
    actual = deffile.html_input(mock_validation(), "checkbox", "hello", "test_value", False, disabled=True)
    expected = '<label><input type="checkbox"  name="hello" value="test_value" disabled="disabled"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_before(self):
    actual = deffile.html_input(mock_validation(), "checkbox", "hello", "test_value", False, before="Button: ")
    expected = '<label>Button: <input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_after(self):
    actual = deffile.html_input(mock_validation(), "checkbox", "hello", "test_value", False, after="</div>")
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_before_after(self):
    actual = deffile.html_input(mock_validation(), "checkbox", "hello", "test_value", False, before="<div>Button: ", after="</div>")
    expected = '<label><div>Button: <input type="checkbox"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_error(self):
    actual = deffile.html_input(mock_validation(errors={"hello":mock_error(message="error")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_warning(self):
    actual = deffile.html_input(mock_validation(warnings={"hello":mock_error(message="warning")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_info(self):
    actual = deffile.html_input(mock_validation(infos={"hello":mock_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_negative(self):
    actual = deffile.html_input(mock_validation(infos={"world":mock_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_double(self):
    actual = deffile.html_input(mock_validation(errors={"hello":mock_error(message="error")}, infos={"hello":mock_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_text_basic(self):
    actual = deffile.html_input(mock_validation(), "text", "hello", "test_value", False)
    expected = '<input type="text"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_text_sized(self):
    actual = deffile.html_input(mock_validation(), "text", "hello", "test_value", False, size="42")
    expected = '<input type="text"  name="hello" value="test_value" size="42">'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_basic(self):
    actual = deffile.html_input(mock_validation(), "textarea", "hello", "test_value", False)
    expected = '<TextArea name="hello">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_sized(self):
    actual = deffile.html_input(mock_validation(), "textarea", "hello", "test_value", False, size="42x42")
    expected = '<TextArea name="hello" cols="42" rows="42">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_button_basic(self):
    actual = deffile.html_input(mock_validation(), "button", "hello", "test_value", False)
    expected = '<input type="button"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_file_basic(self):
    actual = deffile.html_input(mock_validation(), "file", "hello", "test_value", False)
    expected = '<input type="file"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_submit_basic(self):
    actual = deffile.html_input(mock_validation(), "submit", "hello", "test_value", False)
    expected = '<input type="submit"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_hidden_basic(self):
    actual = deffile.html_input(mock_validation(), "hidden", "hello", "test_value", False)
    expected = '<input type="hidden"  name="hello" value="test_value">'
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


  def testReplaceVarsTokenized_Multiple(self):
    actual = deffile.replace_vars_tokenized(["BeginIter", "test-iter-{i}-{j}", '"hello"', ""], {"i":1, "j":2})
    expected = ["BeginIter", "test-iter-1-2", '"hello"', ""]
    self.assertEqual(actual, expected)


  def testReplaceVarsTokenized_Missing(self):
    actual = deffile.replace_vars_tokenized(["BeginIter", "test-iter-{i}-{j}", '"hello"', ""], {"i":1, "k":2})
    expected = ["BeginIter", "test-iter-1-{j}", '"hello"', ""]
    self.assertEqual(actual, expected)


class HtmlMarkTests(unittest.TestCase):


  def testHtmlMark_error(self):
    vm = mock_error("main", "", "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_warning(self):
    vm = mock_error("main", "", "hello")
    actual = deffile.html_mark("?", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">?</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_info(self):
    vm = mock_error("main", "", "hello")
    actual = deffile.html_mark("#", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="info" title="hello">#</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_other(self):
    vm = mock_error("main", "", "hello")
    actual = deffile.html_mark("X", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">X</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_name(self):
    vm = mock_error("", "main", "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a name="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_name_with_href(self):
    vm = mock_error("href", "name", "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a href="href" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


class JsArrayTests(unittest.TestCase):


  def testJsArray(self):
    actual = deffile.js_array([["string1", "string2"]])
    expected = '"string1:string2"'
    self.assertEqual(actual, expected)


  def testJsArrayOverfull(self):
    actual = deffile.js_array([["string1", "string2", "string3"]])
    expected = '"string1:string2"'
    self.assertEqual(actual, expected)


  def testJsArrayMultiple(self):
    actual = deffile.js_array([["string1", "string2"], ["string3", "string4"]])
    expected = '"string1:string2",\n"string3:string4"'
    self.assertEqual(actual, expected)


  def testJsArray3(self):
    actual = deffile.js_array3([["string1", "string2", "string3"]])
    expected = '"string1:string2:string3"'
    self.assertEqual(actual, expected)


  def testJsArray4(self):
    actual = deffile.js_array4([["string1", "string2", "string3", "string4"]])
    expected = '"string1:string2:string3:string4"'
    self.assertEqual(actual, expected)


  def testJsArrayN(self):
    actual = deffile.js_array([["string1", "string2", "string3", "string4", "string5"]], N=5)
    expected = '"string1:string2:string3:string4:string5"'
    self.assertEqual(actual, expected)


  def testJsArrayN_2(self):
    actual = deffile.js_array([["string1", "string2", "string3"], ["string4", "string5", "string6"]], N=3)
    expected = '"string1:string2:string3",\n"string4:string5:string6"'
    self.assertEqual(actual, expected)


### MOCK OBJECTS
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


class os_environ(object):

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
