import unittest

from gmcs import deffile

class HtmlInputTests(unittest.TestCase):
  """
  check, radio, text, textarea, file, button, submit, hidden
  """

  class dummy(object):

    def __init__(self, infos={}, warnings={}, errors={}):
      self.infos = infos
      self.warnings = warnings
      self.errors = errors

  class dummy_error(object):

    def __init__(self, href="", name="", message=""):
      self.href = href
      self.name = name
      self.message = message


  def testHtmlInput_radio_basic(self):
    actual = deffile.html_input(self.dummy(), "radio", "hello", "test_value", False)
    expected = '<label><input type="radio"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_disabled(self):
    actual = deffile.html_input(self.dummy(), "radio", "hello", "test_value", False, disabled=True)
    expected = '<label><input type="radio"  name="hello" value="test_value" disabled="disabled"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_onclick(self):
    actual = deffile.html_input(self.dummy(), "radio", "hello", "test_value", False, onclick="helloworld();")
    expected = '<label><input type="radio"  name="hello" value="test_value" onclick="helloworld();"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_before(self):
    actual = deffile.html_input(self.dummy(), "radio", "hello", "test_value", False, before="Button: ")
    expected = '<label>Button: <input type="radio"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_after(self):
    actual = deffile.html_input(self.dummy(), "radio", "hello", "test_value", False, after="</div>")
    expected = '<label><input type="radio"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_radio_before_after(self):
    actual = deffile.html_input(self.dummy(), "radio", "hello", "test_value", False, before="<div>Button: ", after="</div>")
    expected = '<label><div>Button: <input type="radio"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_basic(self):
    actual = deffile.html_input(self.dummy(), "checkbox", "hello", "test_value", False)
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_disabled(self):
    actual = deffile.html_input(self.dummy(), "checkbox", "hello", "test_value", False, disabled=True)
    expected = '<label><input type="checkbox"  name="hello" value="test_value" disabled="disabled"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_before(self):
    actual = deffile.html_input(self.dummy(), "checkbox", "hello", "test_value", False, before="Button: ")
    expected = '<label>Button: <input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_after(self):
    actual = deffile.html_input(self.dummy(), "checkbox", "hello", "test_value", False, after="</div>")
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_before_after(self):
    actual = deffile.html_input(self.dummy(), "checkbox", "hello", "test_value", False, before="<div>Button: ", after="</div>")
    expected = '<label><div>Button: <input type="checkbox"  name="hello" value="test_value"></div></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_error(self):
    actual = deffile.html_input(self.dummy(errors={"hello":self.dummy_error(message="error")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_warning(self):
    actual = deffile.html_input(self.dummy(warnings={"hello":self.dummy_error(message="warning")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="warning">?</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_info(self):
    actual = deffile.html_input(self.dummy(infos={"hello":self.dummy_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a href="" style="text-decoration:none"><span class="info" title="info">#</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_negative(self):
    actual = deffile.html_input(self.dummy(infos={"world":self.dummy_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_checkbox_marked_double(self):
    actual = deffile.html_input(self.dummy(errors={"hello":self.dummy_error(message="error")}, infos={"hello":self.dummy_error(message="info")}), "checkbox", "hello", "test_value", False)
    expected = '<label><a name="" style="text-decoration:none"><span class="error" title="error">*</span></a><input type="checkbox"  name="hello" value="test_value"></label>'
    self.assertEqual(actual, expected)


  def testHtmlInput_text_basic(self):
    actual = deffile.html_input(self.dummy(), "text", "hello", "test_value", False)
    expected = '<input type="text"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_text_sized(self):
    actual = deffile.html_input(self.dummy(), "text", "hello", "test_value", False, size="42")
    expected = '<input type="text"  name="hello" value="test_value" size="42">'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_basic(self):
    actual = deffile.html_input(self.dummy(), "textarea", "hello", "test_value", False)
    expected = '<TextArea name="hello">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_sized(self):
    actual = deffile.html_input(self.dummy(), "textarea", "hello", "test_value", False, size="42x42")
    expected = '<TextArea name="hello" cols="42" rows="42">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_button_basic(self):
    actual = deffile.html_input(self.dummy(), "button", "hello", "test_value", False)
    expected = '<input type="button"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_file_basic(self):
    actual = deffile.html_input(self.dummy(), "file", "hello", "test_value", False)
    expected = '<input type="file"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_submit_basic(self):
    actual = deffile.html_input(self.dummy(), "submit", "hello", "test_value", False)
    expected = '<input type="submit"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


  def testHtmlInput_hidden_basic(self):
    actual = deffile.html_input(self.dummy(), "hidden", "hello", "test_value", False)
    expected = '<input type="hidden"  name="hello" value="test_value">'
    self.assertEqual(actual, expected)


class HtmlMarkTests(unittest.TestCase):

  class dummy(object):

    def __init__(self, href, name, message):
      self.href = href
      self.name = name
      self.message = message


  def testHtmlMark_error(self):
    vm = self.dummy("main", "", "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_warning(self):
    vm = self.dummy("main", "", "hello")
    actual = deffile.html_mark("?", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">?</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_info(self):
    vm = self.dummy("main", "", "hello")
    actual = deffile.html_mark("#", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="info" title="hello">#</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_other(self):
    vm = self.dummy("main", "", "hello")
    actual = deffile.html_mark("X", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">X</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_name(self):
    vm = self.dummy("", "main", "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a name="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_name_with_href(self):
    vm = self.dummy("href", "name", "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a href="href" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


class JsArrayTests(unittest.TestCase):


  def testJsArray(self):
    actual = deffile.js_array([["string1", "string2"]])
    expected = "'string1:string2'"
    self.assertEqual(actual, expected)


  def testJsArrayOverfull(self):
    actual = deffile.js_array([["string1", "string2", "string3"]])
    expected = "'string1:string2'"
    self.assertEqual(actual, expected)


  def testJsArrayMultiple(self):
    actual = deffile.js_array([["string1", "string2"], ["string3", "string4"]])
    expected = "'string1:string2'\n'string3:string4'"
    self.assertEqual(actual, expected)


  def testJsArray3(self):
    actual = deffile.js_array3([["string1", "string2", "string3"]])
    expected = "'string1:string2:string3'"
    self.assertEqual(actual, expected)


  def testJsArray4(self):
    actual = deffile.js_array4([["string1", "string2", "string3", "string4"]])
    expected = "'string1:string2:string3:string4'"
    self.assertEqual(actual, expected)


  def testJsArrayN(self):
    actual = deffile.js_array([["string1", "string2", "string3", "string4", "string5"]], N=5)
    expected = "'string1:string2:string3:string4:string5'"
    self.assertEqual(actual, expected)


  def testJsArrayN_2(self):
    actual = deffile.js_array([["string1", "string2", "string3"], ["string4", "string5", "string6"]], N=3)
    expected = "'string1:string2:string3'\n'string4:string5:string6'"
    self.assertEqual(actual, expected)
