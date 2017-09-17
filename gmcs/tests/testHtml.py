import unittest

from gmcs import html

from mock import mock_choices, mock_validation, mock_error, os_environ

class HtmlSelectTests(unittest.TestCase):

  def testHtmlSelect_basic(self):
    actual = html.html_select(mock_validation(), "hello")
    expected = '<select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_onfocus(self):
    actual = html.html_select(mock_validation(), "hello", onfocus="test();")
    expected = '<select name="hello" onfocus="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_onchange(self):
    actual = html.html_select(mock_validation(), "hello", onchange="test();")
    expected = '<select name="hello" onchange="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_onfocus_onchange(self):
    actual = html.html_select(mock_validation(), "hello", onfocus="test1();", onchange="test2();")
    expected = '<select name="hello" onfocus="test1();" onchange="test2();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_warning(self):
    actual = html.html_select(mock_validation(warnings={"hello":mock_error(message="warning")}), "hello")
    expected = '<a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_error(self):
    actual = html.html_select(mock_validation(errors={"hello":mock_error(message="error")}), "hello")
    expected = '<a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_info(self):
    actual = html.html_select(mock_validation(infos={"hello":mock_error(message="info")}), "hello")
    expected = '<a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><select name="hello">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_basic(self):
    actual = html.html_select(mock_validation(), "hello", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_onfocus(self):
    actual = html.html_select(mock_validation(), "hello", onfocus="test();", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple"  onfocus="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_onchange(self):
    actual = html.html_select(mock_validation(), "hello", onchange="test();", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple"  onchange="test();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_onfocus_onchange(self):
    actual = html.html_select(mock_validation(), "hello", onfocus="test1();", onchange="test2();", multi=True)
    expected = '<select name="hello" class="multi"  multiple="multiple"  onfocus="test1();" onchange="test2();">'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_warning(self):
    actual = html.html_select(mock_validation(warnings={"hello":mock_error(message="warning")}), "hello", multi=True)
    expected = '<a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_error(self):
    actual = html.html_select(mock_validation(errors={"hello":mock_error(message="error")}), "hello", multi=True)
    expected = '<a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


  def testHtmlSelect_multi_info(self):
    actual = html.html_select(mock_validation(infos={"hello":mock_error(message="info")}), "hello", multi=True)
    expected = '<a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><select name="hello" class="multi"  multiple="multiple" >'
    self.assertEqual(actual, expected)


class HtmlInputTests(unittest.TestCase):
  """
  Input types:
  check, radio, text, textarea, file, button, submit, hidden
  """

  def testHtmlInput_radio_basic(self):
    actual = html.html_input(mock_validation(), "radio", "hello", "test_value", False)
    expected = '<label><input type="radio"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_disabled(self):
    actual = html.html_input(mock_validation(), "radio", "hello", "test_value", False, disabled=True)
    expected = '<label><input type="radio"  name="hello" value="test_value" disabled="disabled"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_onclick(self):
    actual = html.html_input(mock_validation(), "radio", "hello", "test_value", False, onclick="helloworld();")
    expected = '<label><input type="radio"  name="hello" value="test_value" onclick="helloworld();"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_before(self):
    actual = html.html_input(mock_validation(), "radio", "hello", "test_value", False, before="Button: ")
    expected = '<label>Button: <input type="radio"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_after(self):
    actual = html.html_input(mock_validation(), "radio", "hello", "test_value", False, after="</div>")
    expected = '<label><input type="radio"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_before_after(self):
    actual = html.html_input(mock_validation(), "radio", "hello", "test_value", False, before="<div>Button: ", after="</div>")
    expected = '<label><div>Button: <input type="radio"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_basic(self):
    actual = html.html_input(mock_validation(), "checkbox", "hello", "test_value", False)
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_disabled(self):
    actual = html.html_input(mock_validation(), "checkbox", "hello", "test_value", False, disabled=True)
    expected = '<label><input type="checkbox"  name="hello" value="test_value" disabled="disabled"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_before(self):
    actual = html.html_input(mock_validation(), "checkbox", "hello", "test_value", False, before="Button: ")
    expected = '<label>Button: <input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_after(self):
    actual = html.html_input(mock_validation(), "checkbox", "hello", "test_value", False, after="</div>")
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_before_after(self):
    actual = html.html_input(mock_validation(), "checkbox", "hello", "test_value", False, before="<div>Button: ", after="</div>")
    expected = '<label><div>Button: <input type="checkbox"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_error(self):
    actual = html.html_input(mock_validation(errors={"hello":mock_error(message="error")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_warning(self):
    actual = html.html_input(mock_validation(warnings={"hello":mock_error(message="warning")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_info(self):
    actual = html.html_input(mock_validation(infos={"hello":mock_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_negative(self):
    actual = html.html_input(mock_validation(infos={"world":mock_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_double(self):
    actual = html.html_input(mock_validation(errors={"hello":mock_error(message="error")}, infos={"hello":mock_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_text_basic(self):
    actual = html.html_input(mock_validation(), "text", "hello", "test_value", False)
    expected = '<input type="text"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_text_sized(self):
    actual = html.html_input(mock_validation(), "text", "hello", "test_value", False, size="42")
    expected = '<input type="text"  name="hello" value="test_value" size="42">'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_basic(self):
    actual = html.html_input(mock_validation(), "textarea", "hello", "test_value", False)
    expected = '<TextArea name="hello">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_sized(self):
    actual = html.html_input(mock_validation(), "textarea", "hello", "test_value", False, size="42x42")
    expected = '<TextArea name="hello" cols="42" rows="42">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_button_basic(self):
    actual = html.html_input(mock_validation(), "button", "hello", "test_value", False)
    expected = '<input type="button"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_file_basic(self):
    actual = html.html_input(mock_validation(), "file", "hello", "test_value", False)
    expected = '<input type="file"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_submit_basic(self):
    actual = html.html_input(mock_validation(), "submit", "hello", "test_value", False)
    expected = '<input type="submit"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_hidden_basic(self):
    actual = html.html_input(mock_validation(), "hidden", "hello", "test_value", False)
    expected = '<input type="hidden"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


class HtmlMarkTests(unittest.TestCase):

  def testHtmlMark_error(self):
    vm = mock_error("main", "", "hello")
    actual = html.html_mark("*", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_warning(self):
    vm = mock_error("main", "", "hello")
    actual = html.html_mark("?", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">?</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_info(self):
    vm = mock_error("main", "", "hello")
    actual = html.html_mark("#", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="info" title="hello">#</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_other(self):
    vm = mock_error("main", "", "hello")
    actual = html.html_mark("X", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">X</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_name(self):
    vm = mock_error("", "main", "hello")
    actual = html.html_mark("*", vm)
    expected = '<a name="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_name_with_href(self):
    vm = mock_error("href", "name", "hello")
    actual = html.html_mark("*", vm)
    expected = '<a href="href" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


class JsArrayTests(unittest.TestCase):

  def testJsArray(self):
    actual = html.js_array([["string1", "string2"]])
    expected = '"string1:string2"'
    self.assertEqual(actual, expected)


  def testJsArrayOverfull(self):
    actual = html.js_array([["string1", "string2", "string3"]])
    expected = '"string1:string2"'
    self.assertEqual(actual, expected)


  def testJsArrayMultiple(self):
    actual = html.js_array([["string1", "string2"], ["string3", "string4"]])
    expected = '"string1:string2",\n"string3:string4"'
    self.assertEqual(actual, expected)


  def testJsArray3(self):
    actual = html.js_array3([["string1", "string2", "string3"]])
    expected = '"string1:string2:string3"'
    self.assertEqual(actual, expected)


  def testJsArray4(self):
    actual = html.js_array4([["string1", "string2", "string3", "string4"]])
    expected = '"string1:string2:string3:string4"'
    self.assertEqual(actual, expected)


  def testJsArrayN(self):
    actual = html.js_array([["string1", "string2", "string3", "string4", "string5"]], N=5)
    expected = '"string1:string2:string3:string4:string5"'
    self.assertEqual(actual, expected)


  def testJsArrayN_2(self):
    actual = html.js_array([["string1", "string2", "string3"], ["string4", "string5", "string6"]], N=3)
    expected = '"string1:string2:string3",\n"string4:string5:string6"'
    self.assertEqual(actual, expected)
