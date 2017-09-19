"""
html.py

Utilities for HTML formatting
"""

################################################################################
# Constants
ERROR = "*"
WARNING = "?"
INFO = "#"

################################################################################
# Validation methods

def validation_mark(vr, name, info=True):
  """
  Check if there's an error and generate the appropriate error mark
  """
  result = ''
  if name in vr.errors:
    result = html_error_mark(vr.errors[name])
  elif name in vr.warnings:
    result = html_warning_mark(vr.warnings[name])
  elif info and name in vr.infos:
    result = html_info_mark(vr.infos[name])
  return result


def html_mark(mark, vm):
  """
  Return a formatted validation note
  """
  msg = vm.message.replace('"', '&quot;')
  info = mark == INFO
  sort = "name" if not vm.href and not info else "href"
  marker = vm.href or vm.name
  css_class = "info" if info else "error"
  return '<a %s="%s" style="text-decoration:none"><span class="%s" title="%s">%s</span></a>' %\
         (sort, marker, css_class, msg, mark)


def html_error_mark(vm):
  return html_mark(ERROR, vm)

def html_warning_mark(vm):
  return html_mark(WARNING, vm)

def html_info_mark(vm):
  return html_mark(INFO, vm)


def html_input(vr, sort, name, value, checked=False,
               before='', after='', html_class='', title='', size='',
               onclick='', onchange='', disabled=False):
  """
  Return an HTML <input> tag with the specified attributes and
    surrounding text
  TJT 2014-05-07 Adding randid to html_input to pass random number
    matching radio buttons to their labels along
  TJT 2014-09-05 Getting rid of randid to wrap entire radio option in label

  Known types: check, radio, text, textarea, file, button, submit, hidden
  """

  if size:
    if 'x' in size:
      size = ' cols="%s" rows="%s"' % tuple(size.split('x'))
    else:
      size = ' size="' + size + '"'

  if onclick:
    onclick = ' onclick="%s"' % onclick
  if onchange:
    onchange = ' onchange="%s"' % onchange

  chkd = ' checked="checked"' if checked else ''
  dsabld = ' disabled="disabled"' if disabled else ''

  mark = ''
  # TJT 9-16-17 Not checking validation on buttons
  if sort not in ('radio', 'button'):
    mark = validation_mark(vr, name)

  if sort == 'textarea':
    value = value.replace('\\n','\n')
    return '%s%s<TextArea name="%s"%s>%s</TextArea>%s' % \
         (before, mark, name, size, value, after)

  else:
    if html_class:
      html_class = ' class="%s"' % html_class
    if value:
      value = ' value="%s"' % value
    if name:
      name = ' name="%s"' % name
    if title:
      title = ' title="%s"' % title

    output = '%s%s<input type="%s" %s%s%s%s%s%s%s%s%s>%s' % \
         (before, mark, sort, html_class, title, name, value,
          chkd, size, dsabld, onclick, onchange, after)

    # TJT 2014-09-05: If checkbox
    if sort in ('checkbox', 'radio'):
      output = "<label>%s</label>" % output

    return output


# TJT 2014-08-26: Adding onchange
def html_select(vr, name, multi=False, onfocus='', onchange=''):
  """
  Return an HTML <select> tag with the specified name
  """
  mark = validation_mark(vr, name)

  multi_attr = ' class="multi"  multiple="multiple" ' if multi else ''

  if onfocus:
    onfocus = ' onfocus="%s"' % onfocus
  if onchange:
    onchange = ' onchange="%s"' % onchange

  return '%s<select name="%s"%s%s%s>' % \
         (mark, name, multi_attr, onfocus, onchange)


def html_option(vr, name, selected, html, temp=False, strike=False):
  """
  Return an HTML <option> tag with the specified attributes and
  surrounding text
  """
  # TJT 2014-03-19: adding disabled option for always-disabled "future work"
  # TODO: javascript cuts this out, need to change javascript
  if strike:
    strike = ' disabled'
    html = '<p style="display:inline;color:#ADADAD"> %s</p>' % html
  else: strike = ''

  temp = ' class="temp"' or ''
  selected = ' selected' or ''

  return '<option value="%s"%s%s%s>%s</option>' % \
         (name, selected, temp, strike, html)


def html_delbutton(code):
  """
  return the HTML for an iterator delete button that will delete
  iterator "code"
  """
  # TJT 2014-5-27 Regular capital X looks the best + most compliant
  return html_input(None, "button", "", "X",
           html_class="delbutton", title="Delete",
           onclick="remove_element(\'%s\')" % code) + "\n"


def js_array(items, N=2):
  """
  From a list of triples of strings [string1, string2, ...], return
  a string containing a JavaScript-formatted list of strings of the
  form 'string1:string2'.
  """
  return ",\n".join(('"' + ":".join(item[:N]) + '"' for item in items))


def js_array3(items):
  """
  # From a list of triples of strings [string1, string2, ...], return
  # a string containing a JavaScript-formatted list of strings of the
  # form 'string1:string2:string3'. This is used to convey features,
  # values and category (category of feature).
  """
  return js_array(items, N=3)


def js_array4(items):
  """
  # From a list of triples of strings [string1, string2, ...], return
  # a string containing a JavaScript-formatted list of strings of the
  # form 'string1:string2:string3:string4'. This is used to convey features,
  # values, category (category of feature), a flag feature 'customized'.
  """
  return js_array(items, N=4)