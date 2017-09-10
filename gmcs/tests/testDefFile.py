import unittest

from gmcs import deffile

class HtmlInputTests(unittest.TestCase):
  """
  check, radio, textarea, hidden, file, button
  """

  class dummy(object):

    def __init__(self, infos=set(), warnings=set(), errors=set()):
      self.infos = infos
      self.warnings = warnings
      self.errors = errors


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


  def testHtmlInput_textarea_basic(self):
    actual = deffile.html_input(self.dummy(), "textarea", "hello", "test_value", False)
    expected = '<TextArea name="hello">test_value</TextArea>'
    self.assertEqual(actual, expected)


  def testHtmlInput_textarea_size(self):
    actual = deffile.html_input(self.dummy(), "textarea", "hello", "test_value", False, size="40x40")
    expected = '<TextArea name="hello" cols="40" rows="40">test_value</TextArea>'
    self.assertEqual(actual, expected)


class HtmlMarkTests(unittest.TestCase):

  class dummy(object):

    def __init__(self, href, name, message):
      self.href = href
      self.name = name
      self.message = message


  def testHtmlMark_error(self):
    vm = self.dummy("main", False, "hello")
    actual = deffile.html_mark("*", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">*</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_warning(self):
    vm = self.dummy("main", False, "hello")
    actual = deffile.html_mark("?", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">?</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_info(self):
    vm = self.dummy("main", False, "hello")
    actual = deffile.html_mark("#", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="info" title="hello">#</span></a>'
    self.assertEqual(actual, expected)


  def testHtmlMark_other(self):
    vm = self.dummy("main", False, "hello")
    actual = deffile.html_mark("X", vm)
    expected = '<a href="main" style="text-decoration:none"><span class="error" title="hello">X</span></a>'
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
