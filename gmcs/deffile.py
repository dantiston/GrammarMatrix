#!usr/bin/env python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
deffile.py

This module provides the class MatrixDef and supporting methods for validating,
loading, and generating HTML from files defining pages in the matrixdef specification

# TJT 10-10-17 Significantly rewritten and refactored, focused on speed, testability,
  standards compliance, and organization

TODO: Modularize matrixdef files
TODO: Think about either making constants for accessing indices of MatrixDef
      commands or make the commands object oriented (and have accessors)

TODO: PROBLEMS
    * Need to test fix for enhance_choices() re: sentential negation

    * sentences_page
    * more_sentences_page
    * error_page
    * cookie_error_page
    * choices_error_page
    * customize_error_page

    * Parsing/saving should be able to be sped up quite a bit by
        1) making the ChoicesDict an OrderedDict
        2) keep subsection OrderedDicts to allow for faster writing
        3) during saving, only the current section be need to be saved??
            3a) maybe check for enhancements on others, save if changed?

    * fix adjective lrt checkbox so that it can be shown either by a choice
      on the lexicon page or by clicking a button on the morphology page
"""

__authors__ = ["Joshua Crowgey", "Scott Drellishak", "Michael Goodman", "Daniel Mills", "T.J. Trimble"]

######################################################################
# imports

import os
import cgitb
import glob
import re
import tarfile
import gzip
import zipfile
import codecs

from collections import defaultdict, OrderedDict

from gmcs import choices, html, generate
from gmcs.utils import get_name, make_tgz, make_zip
from gmcs.choices import ChoicesFile
from gmcs.validate import ValidationMessage

from jinja2 import Environment, PackageLoader

######################################################################
# HTML blocks, used to create web pages

HTML_jscache = u'''<script type="text/javascript">
// A cache of choices from other subpages
var %s = [
%s
];
</script>'''

HTML_preform = u'<form action="matrix.cgi" method="post" enctype="multipart/form-data" name="choices_form">'

HTML_postform = u'</form>'


######################################################################
# TODO: DELETEME

HTTP_header = 'Content-type: text/html;charset=UTF-8'

HTML_pretitle = '''<!doctype html>
<html>
<head><meta charset="utf-8"/>
'''

HTML_posttitle = '''<script type="text/javascript" src="web/matrix.js">
</script>

<script type="text/javascript">
// An array of strings, each of the form 'name:value|friendly value,...'
var features = [
%s
];

var verb_case_patterns = [
%s
];

var numbers = [
%s
];
</script>

<link rel="stylesheet" href="web/matrix.css">
</head>
'''

HTML_toggle_visible_js = '''<script type="text/javascript">
<!--
    function toggle_visible(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
    }
//-->
</script>
'''

HTML_prebody = '''<body onload="animate(); focus_all_fields(); multi_init(); fill_hidden_errors();scalenav();">
'''

HTML_customprebody = '''<h3>Customized Matrix</h3>

<p>A customized copy of the Matrix has been created for you.
Please download it <a href="%s">here</a>.

<p>This file will be removed from the system in 24 hours.

<h3>Instructions</h3>

<p>To unpack the archive, if your browser hasn't already done it for
you, first try saving it on your desktop and double-clicking it.  If
that doesn't work, and you're using Linux or Mac OS X, from a command
prompt, type <tt>tar xzf matrix.tar.gz</tt> or <tt>unzip matrix.zip</tt>.

<p>Once you've unpacked the archive you should find a directory called
<tt>matrix</tt>.  Inside the directory are several files.  Here is
an explanation of some:

<ul>
<li><tt>matrix.tdl</tt>: Language independent type and constraint
definitions.  You should not need to modify this file.
<li><tt>my_language.tdl</tt>: Types and constraints specific to your
language.  (Actual file name depends on the name of your language.)
<li><tt>lexicon.tdl</tt>: Lexical entries for your language.
<li><tt>rules.tdl</tt>: Phrase structure rule instance entries for
your language.
<li><tt>irules.tdl</tt>: Spelling-changing lexical rule instance
entries for your language.
<li><tt>lrules.tdl</tt>: Non-spelling-changing lexical rule instance
entries for your language.
<li><tt>lkb/script</tt>: The script file for loading your grammar into
the LKB.
<li><tt>choices</tt>: A record of the information you
provided in the matrix configuration form.
</ul>

<p>To run this grammar, start the LKB, and the load it by selected
"Load > Complete grammar..." from the LKB menu.  You can then parse a
sentence by selecting "Parse > Parse input..." from the LKB menu.  The
dialog box that pops up should include the sentences you filled into
the form.  When a sentence parses successfully, you can try generating
from the resulting semantic representation by selecting "Generate" or
"Generate from edge" from the pop-up menu.  For more on using the LKB,
see the <a href="http://www.delph-in.net/lkb">LKB page</a> and/or
Copestake 2002 <a
href="http://cslipublications.stanford.edu/lkb.html"><i>Implementing
Typed Feature Structure Grammars</i></a>.

<hr>
<a href="matrix.cgi">Back to form</a><br>
<a href="http://www.delph-in.net/matrix/">Back to Matrix main page</a><br>
<a href="http://www.delph-in.net/lkb">To the LKB page</a>
'''

HTML_postbody = '''</body>

</html>'''

######################################################################
# Constants
COMMENT_CHAR = u"#"

HTTP_COOKIE = u"HTTP_COOKIE"

######################################################################
# Jinja
jinja = Environment(loader=PackageLoader('gmcs', 'html'))


######################################################################
# Helper functions

def tokenize_def_line(line):
  """
  Split a line of matrixdef into tokens, treating double-quoted strings as
  single tokens.
  """
  i = 0
  length = len(line)
  result = []

  while i < length:
    # skip whitespace
    while i < length and line[i].isspace():
      i += 1
    # if it's quoted, read to the close quote, otherwise to a space
    if i < length:
      if line[i] == u'"':
        i += 1
        start = i
        while i < length and not (line[i] == u'"' and line[i-1] != '\\'):
          i += 1
        result.append(line[start:i].replace(u'\\"', u'"'))
        i += 1
      else:
        start = i
        while i < length and not line[i].isspace():
          i += 1
        result.append(line[start:i])

  return result


def merge_quoted_strings(document):
  """
  given a list of lines of text, some of which may contain
  unterminated double-quoted strings, merge some lines as necessary so
  that every quoted string is contained on a single line, and return
  the merged list
  """
  i = 0
  j = 0
  in_quotes = False
  doc_length = len(document)
  while i < doc_length:
    line = document[i]
    length = len(line)

    while j < length:
      if line[j] == u'"' and (j == 0 or line[j-1] != u'\\'):
        in_quotes = not in_quotes
      j += 1

    # if we reach the end of a line inside a quoted string, merge with
    # the next line and reprocess the newly-merged line
    if in_quotes:
      try:
        document[i] += document[i+1] # crash here implies an unbalanced '"'
        del document[i+1]
        doc_length -= 1
      except IndexError as e:
        raise ValueError("Unbalanced parentheses in matrix definition file")
    else:
      j = 0
      i += 1

  return document


def replace_vars(line, iter_vars):
  """
  Replace variables of the form "{name}" in line using the dict iter_vars
  """
  for k in iter_vars:
    line = re.sub(u'\\{' + k + u'\\}', str(iter_vars[k]), line)
  return line


def replace_vars_tokenized(line, iter_vars):
  """
  Replace variables of the form "{name}" in line using the dict iter_vars
  """
  regexes = compile_string_keys(iter_vars)
  result = (list(line[0]), line[1], line[2])
  # modifying result in place, so don't iterate through its elements
  for i in range(len(result[0])):
    for k, v in iter_vars.items():
        result[0][i] = regexes[k].sub(str(v), result[0][i])
  return result


def compile_string_keys(regexes):
  result = {}
  for regex in regexes:
    result[regex] = re.compile(u"\\{%s\\}" % regex)
  return result


######################################################################
# Valid commands

SECTION = u'Section'
TEXT = u'Text'
TEXT_AREA = u'TextArea'
CHECK = u'Check'
RADIO = u'Radio'
BULLET = u'.'
BUTTON = u'Button'
FILE = u'File'

LABEL = u'Label'
HIDDEN = u'Hidden'
SEPARATOR = u'Separator'

CACHE = u'Cache'

SELECT = u'Select'
MULTI_SELECT = u'MultiSelect'
BEGIN_ITER = u'BeginIter'
END_ITER = u'EndIter'

commands = set([SECTION, TEXT, TEXT_AREA, CHECK, RADIO, BUTTON, FILE, LABEL,
                HIDDEN, SEPARATOR, CACHE, SELECT, MULTI_SELECT, BEGIN_ITER, END_ITER])


######################################################################
# MatrixDef class

class MatrixDef:
  """
  This class and its methods are used to parse Matrix definition
  formatted files (currently just the file ./matrixdef), and based
  on the contents, to produce HTML pages and save choices files.
  """

  SECTION_VARIABLE_NAME = 1
  SECTION_FRIENDLY_NAME = 2
  SECTION_DOC_LINK = 3
  SECTION_SHORT_FRIENDLY_NAME = 4
  SECTION_ONLOAD = 5
  SECTION_SKIP = 6

  TOKENIZED_LINES = "tokenized_lines"
  SECTIONS = "sections"
  SECTION_NAMES = "section_names"
  DOC_LINKS = "doc_links"
  SHORT_NAMES = "short_names"
  HIDE_ON_NAVIGATION = "hide_on_navigation"
  F2V = "f2v"
  V2F = "v2f"


  def __init__(self, def_file):
    # Define members
    self.section_names = {}
    self.doc_links = {}
    self.short_names = {}

    # Allow initialization of empty file for testing
    if def_file:
      self.load(def_file)
    else:
      self.v2f = defaultdict(lambda key: key)
      self.f2v = defaultdict(lambda key: key)

    self.load_html_generators()


  def __getstate__(self):
    """
    Pickling MatrixDef only stores the definition data
    """
    result = {}
    result[self.TOKENIZED_LINES] = self.tokenized_lines
    result[self.SECTIONS] = self.sections

    result[self.SECTION_NAMES] = self.section_names
    result[self.DOC_LINKS] = self.doc_links
    result[self.SHORT_NAMES] = self.short_names
    result[self.HIDE_ON_NAVIGATION] = self.hide_on_navigation

    result[self.F2V] = self.f2v
    result[self.V2F] = self.v2f
    return result


  def __setstate__(self, state):
    """
    Unpickling MatrixDef only retrives the definition data
    """
    self.__dict__.update(state)
    self.load_html_generators()


  def load_html_generators(self):
    self.html_gens = {
      BEGIN_ITER: self.iter_to_html,
      CACHE: self.cache_to_html,
      LABEL: self.label_to_html,
      SEPARATOR: self.separator_to_html,
      CHECK: self.check_to_html,
      RADIO: self.radio_to_html,
      HIDDEN: self.hidden_to_html,
      FILE: self.file_to_html,
      BUTTON: self.button_to_html,
      SELECT: self.select_to_html,
      MULTI_SELECT: self.select_to_html,
      TEXT: self.text_to_html,
      TEXT_AREA: self.text_to_html
    }


  def load(self, def_file):
    """
    (Re)load a matrixdef file to this MatrixDef
    """
    self.def_file = def_file
    with codecs.open(self.def_file, 'r', encoding="utf-8") as f:
      self.__load_file(f)

    self.make_name_map()


  def __load_file(self, f):
    """
    Load the matrixdef file into memory
    """
    def_lines = merge_quoted_strings(f.readlines())
    # Remove unimportant whitespace
    def_lines = map(unicode.strip, def_lines)
    # Remove empty lines and comments
    def_lines = (line for line in def_lines if line and not line[0] == COMMENT_CHAR)
    # Tokenize and count ONCE
    tokenized_lines = (tokenize_def_line(line) for line in def_lines)
    self.tokenized_lines = [(line, len(line), line[0]) for line in tokenized_lines]

    # Keep track of which sections to not show on navigation
    self.hide_on_navigation = set()

    self.sections = OrderedDict() # Keep track of order
    last = -1
    section_name = None
    for i, (line, word_length, element) in enumerate(self.tokenized_lines):
      if element == SECTION:
        # Save previous
        if last >= 0:
          self.sections[section_name] = self.tokenized_lines[last:i]
        last = i
        # Prepare for the next
        section_name = line[self.SECTION_VARIABLE_NAME]
        # Support section definition syntax
        if len(line) >= 3:
          self.section_names[section_name] = line[self.SECTION_FRIENDLY_NAME]
          self.doc_links[section_name] = line[self.SECTION_DOC_LINK]
          if len(line) >= 5:
            self.short_names[section_name] = line[self.SECTION_SHORT_FRIENDLY_NAME]
            # Ignore onload for now
            if len(line) >= 7:
              self.hide_on_navigation.add(section_name)
    if last != len(self):
      self.sections[section_name] = self.tokenized_lines[last:]


  def __len__(self):
    return len(self.tokenized_lines)


  ######################################################################
  # Variable/friendly name mapping

  FRIENDLY_NAME_ELEMENTS = (TEXT, TEXT_AREA, CHECK, RADIO, SELECT, MULTI_SELECT, BULLET)

  def make_name_map(self):
    """
    initialize the variable to friendly name (v2f) and
    friendly name to variable (f2v) mappings
    """
    self.v2f = {}
    self.f2v = {}
    for word, word_length, element in self.tokenized_lines:
      if len(word) >= 3:
        variable_name, friendly_name = word[1:3]
        if element in self.FRIENDLY_NAME_ELEMENTS:
          self.v2f[variable_name] = friendly_name
          self.f2v[friendly_name] = variable_name


  def f(self, v):
    """
    return the friendly name for a variable, or the variable if none is defined
    """
    return self.v2f[v] if v in self.v2f else v


  def v(self, f):
    """
    return the variable for a friendly name, or the friendly name if none is defined
    """
    return self.f2v[v] if v in self.f2v else v


  ######################################################################
  # Utility methods

  # TJT 2014-08-28: Adding method to find if some choice exists
  # in order to enable skipping UI elements based on this choice
  def check_choice_switch(self, switch, choices):
    """
    This method checks to see if a given string or regex (the switch)
    is in a given choices file. This method is used to see if a given
    UI element should be skipped. As such, the boolean return value
    is a little bit backwards. The function returns True if the switch
    is not found, and false if it is found.
    TODO: This can be simplified
    """
    if not switch:
      return True
    # Switch can have multiple variable names
    switches = switch.strip('"').split('|')
    # Switch contains choice name and value
    # split on the rightmost "=" just in case...
    # TODO: This can be simplified
    switches = [switch.rsplit('=', 1) if "=" in switch else switch
                for switch in switches]
    # Default to true
    # TODO: This dict can be removed, just return false when setting values to false
    skip_it = {}
    for switch in switches:
      if isinstance(switch, list):
        skip_it[switch[0]] = True
      else:
        skip_it[switch] = True
    for instance in switches:
      if isinstance(instance, list):
        switch = instance[0].strip()
        values = instance[1].strip().strip("()").split(',') # Get multiple values
      else:
        switch = instance
        values = False # set default

      results = choices.get_regex(switch)
      if results:
        # Found a match
        if not values:
          # If no value, then switching on a key,
          # which was found, so don't skip it!
          skip_it[switch] = False
        else:
          for item in results:
            # Values is almost gauranteed to be small, no need to make it a set
            if item[1] in values:
              skip_it[switch] = False
              break
    # if all false, don't skip it
    # else, skip it
    return any(skip_it.values())


  #############################################################################
  # Page methods

  def main_page(self, cookie, vr, choices=None):
    """
    Create and print the main matrix page.  The argument is a cookie
    that determines where to look for the choices file.
    """

    choices = []
    choices_file = self.get_choices_file_from_session(cookie, choices)
    if choices_file and os.path.exists(choices_file):
      with codecs.open(choices_file, 'r', encoding='utf-8') as f:
        choices = f.readlines()

    template = jinja.get_template('main.html')
    return template.render(
        cookie=cookie,
        datestamp=self.get_datestamp(),
        navigation=self.page_links(vr, choices),
        download_grammar=self.download_links(vr),
        choices_file=choices_file,
        upload_choices=self.upload_links(vr),
        sample_grammars=self.sample_grammars()
    )


  def sub_page(self, section, cookie, vr, choices=None):
    """
    Create and print the matrix subpage for the specified section
    based on the arguments, which are the name of the section and
    a cookie that determines where to look for the choices file
    """

    tokenized_section_def = self.sections[section]

    choices, choices_file = self.get_choices_from_session(cookie, choices)

    template = jinja.get_template('sub.html')
    return template.render(
        title=self.section_names[section],
        features=html.js_array4_skip3(choices.features()),
        verb_case_patterns=html.js_array([c for c in choices.patterns() if not c[2]]),
        numbers=html.js_array(choices.numbers()),
        onload=self.get_onload(tokenized_section_def),
        cookie=cookie,
        section=section,
        section_name=self.section_names[section],
        section_doc_link=self.doc_links[section],
        navigation=self.navigation(vr, choices_file, section=section),
        form=self.defs_to_html(tokenized_section_def, choices, vr, '', {})
    )


  def custom_page(self, session_path, grammar_path, arch_type):
    """
    Create and print the "download your matrix here" page for the
    customized matrix in the directory specified by session_path
    """

    grammar_dir = grammar_path.replace(session_path, '').lstrip('/')
    arch_file = grammar_dir + ('.tar.gz' if arch_type == u'tgz' else '.zip')
    cwd = os.getcwd()
    os.chdir(session_path)
    if arch_type == u'tgz':
      make_tgz(grammar_dir)
    else:
      make_zip(grammar_dir)
    os.chdir(cwd)

    template = jinja.get_template('customized.html')
    return template.render(
        section_name=u"Matrix Customized",
        grammar_link=os.path.join(session_path, arch_file),
        cookie=session_path[-4:]
    )


  def sentences_page(self, session_path, grammar_dir, session):
    """
    Generate and print sample sentences from the customized grammar
    TODO: Write unit test for this
    """
    print HTTP_header + '\n'
    print HTML_pretitle
    print '<title>Matrix Sample Sentences</title>'
    print HTML_posttitle
    delphin_dir = os.path.join(os.getcwd(), 'delphin')
    sentences = generate.get_sentences(grammar_dir, delphin_dir, session)
    print HTML_sentencesprebody
    for i in range(len(sentences)):
      long = False
      print "<b>" + sentences[i][0][0][4:]+"</b> " + sentences[i][0][2] + ", with predication: " + ", ".join(sentences[i][0][1].values()) +"<br>"
      if len(sentences[i][1]) > 0 and sentences[i][1][0] == u'#EDGE-ERROR#':
        print 'This grammar combined with this input semantics results in too large of a seach space<br>'
      elif len(sentences[i][1]) > 0 and sentences[i][1][0] == u'#NO-SENTENCES#':
        print 'This combination of verb, pattern, and feature specification did not result in any generated sentences with the nouns that the system chose.<br>'
        print HTML_preform
        print '<input type="hidden" name="verbpred" value="%s">' % sentences[i][0][1]
        print '<input type="hidden" name="template" value="%s">' % sentences[i][0][3]
        print '<input type="hidden" name="grammar" value="%s">' % grammar_dir
        print '<input type="submit" name="" value="Try this verb and pattern with all possible nouns">'
        print HTML_postform
      else:
        for j in range(len(sentences[i][1])):
          if j == 10:
            print '<div id="%s_extra" style=display:none;>' % (i+1)
            long = True
          print '<div onclick=toggle_visibility(["%s_%s_parsemrs"])>%s. %s</div>' % (i+1,j+1,j+1,sentences[i][1][j])
          print '<div id="%s_%s_parsemrs" style=display:none;>' % (i+1,j+1)
          print '&nbsp&nbsp Parse tree:<br>' + sentences[i][2][j]
          print '&nbsp&nbsp MRS:<br>' + sentences[i][3][j]
          print '</div>'
        if long:
          print '</div>'
          print '<div id="%s_dots" style=display:block;>...</div>' % (i+1)
          print '<input type="button" id="%s_show" value="Show Remainder" onclick=toggle_visibility(["%s_extra","%s_dots","%s_show","%s_hide"]) style=display:block;>' % (i+1,i+1,i+1,i+1,i+1)
          print '<input type="button" id="%s_hide" value="Hide Remainder" onclick=toggle_visibility(["%s_extra","%s_dots","%s_show","%s_hide"]) style=display:none;>' % (i+1,i+1,i+1,i+1,i+1)

        print '<br>'
        print HTML_preform
        print '<input type="hidden" name="verbpred" value="%s">' % sentences[i][0][1]
        print '<input type="hidden" name="template" value="%s">' % sentences[i][0][3]
        print '<input type="hidden" name="grammar" value="%s">' % grammar_dir
        print '<input type="submit" name="" value="More sentences with this verb and pattern">'
        print HTML_postform
      print '<br>'
    print HTML_sentencespostbody
    print HTML_postbody


  def more_sentences_page(self, session_path, grammar_dir, verbpred, template_file, session):
    """
    Display page with additional sentences
    """
    print HTTP_header + '\n'
    print HTML_pretitle
    print '<title>More Sentences</title>'
    print HTML_sentencesprebody
    delphin_dir = os.path.join(os.getcwd(), 'delphin')
    sentences, trees, mrss = generate.get_additional_sentences(grammar_dir,
                                                               delphin_dir,
                                                               verbpred,
                                                               template_file,
                                                               session)
    if len(sentences) > 0:
      if sentences[0] == u"#EDGE-ERROR#":
        print 'This grammar combined with this input semantics results in too large of a search space<br>'
      if sentences[0] == u"#NO-SENTENCES#":
        print 'This combination of verb, pattern, and feature specification did not result in any generated sentences.<br>'
      else:
        for j in range(len(sentences)):
          #print str(j+1) + '. <span title="' + trees[j] + '">' + sentences[j] + "</span><br>"
          print '<div onclick=toggle_visibility(["%s_parsemrs"])>%s. %s</div>' % (j+1,j+1,sentences[j])
          print '<div id="%s_parsemrs" style=display:none;>' % (j+1)
          print '&nbsp&nbsp Parse tree:<br>' + trees[j]
          print '&nbsp&nbsp MRS:<br>' + mrss[j]
          print '</div>'
    print '<br><input type="button" name="" value="Back to sentences" onclick="history.go(-1)">'
    print HTML_sentencespostbody
    print HTML_postbody


  def error_page(self, vr):
    """
    Display errors and warnings that occurred during customization
    """
    print HTTP_header + '\n'
    print HTML_pretitle
    print '<title>Matrix Customization Errors</title>'
    print HTML_prebody

    if vr.has_errors():
      print '<h2>Errors</h2>'
      print '<dl>'
      for k in vr.errors:
        print '<dt><b>' + k + ':</b></dt>'
        print '<dd>' + vr.errors[k].message + '</dd>'
      print '</dl>'

    if vr.has_warnings():
      print '<h2>Warnings</h2>'
      print '<dl>'
      for k in vr.warnings:
        print '<dt><b>' + k + ':</b></dt>'
        print '<dd>' + vr.warnings[k].message + '</dd>'
      print '</dl>'

    print HTML_postbody


  def cookie_error_page(self):
    """
    Inform the user that cookies must be enabled
    """
    print HTTP_header + '\n'
    print HTML_pretitle
    print '<title>Cookies Required</title>'
    print HTML_prebody

    print '<div style="position:absolute; top:45%; width:100%">\n' + \
          '<p style="color:red; text-align:center; font-size:16pt">' + \
          'Cookies must be enabled for this site in your browser in order ' + \
          'to fill out the questionnaire.</p>\n'
    print '<p style="text-align:center; font-size:16pt">'
    print 'If cookies are enabled, try reloading an '
    print '<a href="matrix.cgi?choices=empty">empty questionnaire</a>. '
    print 'Note that any existing changes will be lost.</p>'
    print '</div>'

    print HTML_postbody


  def choices_error_page(self, choices_file, exc=None):
    print HTTP_header + '\n'
    print HTML_pretitle
    print '<title>Invalid Choices File</title>'
    print HTML_posttitle % ('', '', '')
    print HTML_toggle_visible_js
    print HTML_prebody

    print '<div style="position:absolute; top:15%; width:60%">\n' + \
          '<p style="color:red; text-align:center; font-size:12pt">' + \
          'The provided choices file is invalid. If you have edited the ' +\
          'file by hand, please review the changes you made to make sure ' +\
          'they follow the choices file file format. If you did not make ' +\
          'any manual changes, please email the choices file to the Matrix ' +\
          'developers. You may download the choices file to try and fix ' +\
          'any errors.</p>\n'

    print '<p style="text-align:center"><a href="' + choices_file + '">' +\
          'View Choices File</a> (right-click to download)</p>'

    print '<p style="text-align:center">In most cases, you can go back ' +\
          'in your browser and fix the problems, but if not you may ' +\
          '<a href="matrix.cgi?choices=empty">reload an empty ' +\
          'questionnaire</a> (this will erase your changes, so be sure to ' +\
          'save your choices (above) first).'
    exception_html(exc)
    print HTML_postbody


  def customize_error_page(self, choices_file, exc=None):
    print HTTP_header + '\n'
    print HTML_pretitle
    print '<title>Problem Customizing Grammar</title>'
    print HTML_posttitle % ('', '', '')
    print HTML_toggle_visible_js
    print HTML_prebody

    print '<div style="position:absolute; top:15%; width:60%">\n' +\
          '<p style="color:red; text-align:center; font-size:12pt">' +\
          'The Grammar Matrix Customization System was unable to create ' +\
          'a grammar with the provided choices file. You may go back in ' +\
          'your browser to try and fix the problem, or if you think ' +\
          'there is a bug in the system you may email the choices file ' +\
          'to the developers</p>\n'

    print '<p style="text-align:center"><a href="' + choices_file + '">' +\
          'View Choices File</a> (right-click to download)</p>'

    print '<p style="text-align:center">In most cases, you can go back ' +\
          'in your browser and fix the problems, but if not you may ' +\
          '<a href="matrix.cgi?choices=empty">reload an empty ' +\
          'questionnaire</a> (this will erase your changes, so be sure to ' +\
          'save your choices (above) first).'
    exception_html(exc)
    print HTML_postbody


  ##############################################################################
  # Page components
  def get_choices_from_session(self, session, choices):
    """
    Load the choices file from the given session directory
    """
    choices_file = self.get_choices_file_from_session(session, choices)
    if not choices:
      choices = ChoicesFile(choices_file)
    return choices, choices_file


  def get_choices_file_from_session(self, session, choices):
    """
    Get the choices file path from the session
    """
    result = u'' # Default to empty for testing
    if not choices:
      result = os.path.join(u'sessions', session, u'choices')
    return result


  def get_datestamp(self):
    """
    Load the datestamp
    """
    try:
      with codecs.open('datestamp', 'r', encoding="utf-8") as f:
        return f.readline().strip()
    except:
      return u"[date unknown]"


  def get_onload(self, tokenized_section_def):
    """
    Get the onload JavaScript event for the given section
    """
    result = u""
    if tokenized_section_def[0][1] > self.SECTION_ONLOAD:
      result = tokenized_section_def[0][0][self.SECTION_ONLOAD]
    return result


  def page_links(self, vr, choices):
    """
    Get the page links for the main page with the specified
    validation errors and choices
    """
    # TODO: This is very similar to what happens in navigation()... break it out?
    # pass through the definition file once, augmenting the list of validation
    # results with section names so that we can put red asterisks on the links
    # to the assocated sub-pages on the main page.
    result = []

    # Check for validation issues # TODO: Break this out
    prefix = u''
    for word, word_length, element in self.tokenized_lines:
      if word_length < 2:
        continue

      elif element == SECTION:
        cur_sec = word[1]

      elif element == BEGIN_ITER:
        if prefix:
          prefix += u'_'
        prefix += re.sub(u'\\{.*\\}', u'[0-9]+', word[1])

      elif element == END_ITER:
        prefix = re.sub(u'_?' + word[1] + u'[^_]*$', '', prefix)

      elif not (element == LABEL and word_length < 3):
        pat = u'^' + prefix
        if prefix:
          pat += u'_'
        pat += word[1] + '$'
        # TODO: This could be made more efficient
        for k in vr.errors.keys():
          if re.search(pat, k):
            anchor = u"matrix.cgi?subpage="+cur_sec+"#"+k
            vr.err(cur_sec, "This section contains one or more errors. \nClicking this error will link to the error on the subpage.", anchor+"_error", False)
            break
        for k in vr.warnings.keys():
          if re.search(pat, k):
            anchor = u"matrix.cgi?subpage="+cur_sec+"#"+k
            vr.warn(cur_sec, "This section contains one or more warnings. \nClicking this warning will link to the warning on the subpage.", anchor+"_warning", False)
            break

    for section_name in self.sections:
      result.append(u'<div class="section"><span id="' + section_name + u'button" ' + \
            u'onclick="toggle_display(\'' + \
            section_name + u'\',\'' + section_name + u'button\')"' + \
            u'>&#9658;</span>\n')
      result.append(html.validation_mark(vr, section_name, info=False))
      result.append(u'<a href="matrix.cgi?subpage=%s">%s</a>\n' % (section_name, self.section_names[section_name]))
      result.append(u'<div class="values" id="%s" style="display:none;">' % section_name)

      cur_sec = u''
      printed_something = False
      for c in choices:
        try:
          c = c.strip()
          if c:
            a, v = c.split('=', 1)
            if a == u'section':
              cur_sec = v.strip()
            elif cur_sec == section_name:
              result.append(self.f(a) + u' = ' + self.f(v) + u'<br>')
              printed_something = True
            # TODO: Confirm this
            # else if printed_something:
            #   break
        except ValueError:
          if cur_sec == section_name:
            result.append(u'(<i>Bad line in choices file: </i>"<tt>' + \
                          c + u'</tt>")<br>')
            printed_something = True

      if not printed_something:
        result.append(u'&nbsp;')
      result.append(u'</div></div>\n')

    return u"".join(result)


  def download_links(self, vr):
    """
    the buttons after the subpages
    """
    result = []
    result.append(html.html_input(vr, 'hidden', 'customize', 'customize'))
    result.append(html.html_input(vr, 'radio', 'delivery', 'tgz',
                             checked=True, before='Archive type: ', after=' .tar.gz'))
    result.append(html.html_input(vr, 'radio', 'delivery', 'zip', after=' .zip'))
    result.append(u"<br>")
    result.append(html.html_input(vr, 'submit', 'create_grammar_submit', 'Create Grammar',
                             disabled=vr.has_errors()))
    result.append(html.html_input(vr, 'submit', 'sentences', 'Test by Generation',
                             disabled=vr.has_errors()))
    return u"\n".join(result)


  def upload_links(self, vr):
    """
    the FORM for uploading a choices file
    """
    result = []
    result.append(html.html_input(vr, 'submit', '', 'Upload Choices File:', False, '<p>', ''))
    result.append(html.html_input(vr, 'file', 'choices', '', False, '', '</p>', ''))
    return u"".join(result)


  def sample_grammars(self):
    """
    the list of sample choices files
    """
    result = []
    if os.path.exists('web/sample-choices'):
      result.append(u'<h3>Sample Grammars:</h3>\n')
      result.append(u'<p>Click a link below to have the questionnaire ' + \
                    u'filled out automatically.</p>\n')
      result.append(u'<p>\n')

      linklist = {}

      for path in glob.iglob('web/sample-choices/*'):
        path = path.replace(u'\\', u'/')
        lang = choices.get_choice('language', path) or u'(empty questionnaire)'
        if lang == u'minimal-grammar': lang = u'(minimal grammar)'
        linklist[lang] = path

      for k in sorted(linklist.keys(), lambda x, y: cmp(x.lower(), y.lower())):
        result.append(u'<a href="matrix.cgi?choices=%s">%s</a><br />\n' % (linklist[k], k))

      result.append(u'</p>')
    return u"".join(result)


  def navigation(self, vr, choices_file, section=None):
    """
    Pass through the definition file once, augmenting the list of validation
    results with section names so that we can put red asterisks on the links
    to the assocated sub-pages on the nav menu.

    TODO: Simplify this
    """

    # Get the validation
    prefix = u''
    sec_links = []
    n = -1
    printed = False
    for word, word_length, element in self.tokenized_lines:
      cur_sec = u''

      if word_length < 2:
        continue

      elif element == SECTION:
        printed = False
        cur_sec = word[1]
        # If marked hidden, don't show it in navigation
        if cur_sec not in self.hide_on_navigation:
          # disable the link if this is the page we're on
          # TODO: Change how this span tag is being opened and closed
          shortname = u" data-short-name=\"%s\"" % self.short_names[cur_sec] if cur_sec in self.short_names else u""
          if cur_sec == section:
            sec_links.append(u'</span><span data-name="%s"%s class="navlinks">%s</span>' % (self.section_names[cur_sec], shortname, self.section_names[cur_sec]))
          else:
            sec_links.append(u'</span><a data-name="%s"%s class="navlinks" href="#" onclick="submit_go(\'%s\')">%s</a>' % (self.section_names[cur_sec], shortname, cur_sec, self.section_names[cur_sec]))
          n += 1

      elif element == BEGIN_ITER:
        if prefix:
          prefix += u'_'
        prefix += re.sub('\\{.*\\}', '[0-9]+', word[1])

      elif element == END_ITER:
        prefix = re.sub('_?' + word[1] + '[^_]*$', '', prefix)

      elif not (element == LABEL and word_length < 3):
        pattern = u'^' + prefix
        if prefix:
          pattern += u'_'
        pattern += word[1] + u'$'

        # TODO: This could be made more efficient
        # Add errors to the links
        if not printed:
          for k in vr.errors:
            if re.search(pattern, k):
              sec_links[n] = html.ERROR + sec_links[n]
              printed = True
              break
        if not printed:
          for k in vr.warnings:
            if re.search(pattern, k):
              sec_links[n] = html.WARNING + sec_links[n]
              printed = True
              break


    # Generate the result
    result = []
    result.append(u'<div id="navmenu"><br />')
    result.append(u'<a href="." onclick="submit_main()" class="navleft">Main page</a><br />')
    result.append(u'<hr />')
    for l in sec_links:
      # TODO: Change how this span tag is being opened and closed
      result.append(u'<span style="color:#ff0000;" class="navleft">'+l+'<br />')

    result.append(u'<hr />')
    result.append(u'<a href="' + choices_file + u'" class="navleft">Choices file</a><br /><div class="navleft" style="margin-bottom:0;padding-bottom:0">(right-click to download)</div>')
    result.append(u'<a href="#stay" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />')
    # TJT 2014-05-28: Not sure why the following doesn't work -- need to do more investigation
    #result.append('<a href="?subpage=%s" onclick="document.forms[0].submit()" class="navleft">Save &amp; stay</a><br />' % section)

    ## if there are errors, then we mark them on the links (the links in red and unclickable)
    if vr.has_errors():
      result.append(u'<span class="navleft">Create grammar:')
      result.append(html.html_info_mark(ValidationMessage(u'', u'Resolve validation errors to enable grammar customization.', u'')))
      result.append(u'</span><br />')
      result.append(u'<span class="navleft" style="padding-left:15px">tgz</span>, <span class="navleft">zip</span>')
    else:
      result.append(u'<span class="navleft">Create grammar:</span><br />')
      result.append(u'<a href="#" onclick="nav_customize(\'tgz\')" class="navleft" style="padding-left:15px">tgz</a>, <a href="#customize" onclick="nav_customize(\'zip\')" class="navleft">zip</a>')

    result.append(u'</div>')
    return u"\n".join(result)



  ##############################################################################
  # matrixdef to HTML methods

  # TJT 2017-09-09: Defining this once for efficiency's sake
  fillstrings = {'fillregex':'fill_regex(%(args)s)',
                 'fillnames':'fill_feature_names(%(args)s)',
                 'fillnames2':'fill_feature_names_only_customized(%(args)s)',
                 'fillvalues':'fill_feature_values(%(args)s)',
                 'fillverbpat':'fill_case_patterns(false)',
                 'fillnumbers':'fill_numbers()',
                 'fillcache':'fill_cache(%(args)s)'}


  def defs_to_html(self, tokenized_lines, choices, vr, prefix, variables, do_replace=False):
    """
    Turn a list of lines containing matrix definitions into a string
    containing HTML

    This method calls out to the various *_to_html methods via
    the function pointer dictionary at self.html_gens, popualted
    in self.__init__()

    TODO: Store this in a variable
    TODO: Pickle this? This would require a compile step + a choice loading step
    TODO: Write a syntax checker... maybe make this a syntax checker?
    """

    cookie = self.get_cookie()

    num_lines = len(tokenized_lines)

    page = u""
    i = 0
    while i < num_lines:
      word, word_length, element = self.__get_word(tokenized_lines, i, variables=variables, do_replace=do_replace)
      if word:
        if element in self.html_gens:
          word, word_length, element, i, result = self.html_gens[element](
              tokenized_lines, choices, vr, cookie, prefix, variables,
              num_lines, word, word_length, element, i, do_replace=do_replace)
          page += result

      i += 1

    return page


  def check_syntax(self, tokenized_lines):
    """
    Simple tool to load in tokenized lines and see if they are valid or not
    """
    try:
      self.defs_to_html(tokenized_lines, choices, vr, prefix, variables)
    except MatrixDefSyntaxException as e:
      print "MatrixDefSyntaxException: %s" % e.message
      return False
    return True


  def button_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    if word_length < 5:
      # TODO: Technically, before and after should be optional
      raise MatrixDefSyntaxException("Button improperly defined: %s; expected at least 5 tokens, got %s" % (word, word_length))
    vn, bf, af, oc = word[1:]
    result = html.html_input(vr, element.lower(), '', vn, False, bf, af, onclick=oc) + '\n'
    return word, word_length, element, i, result


  def cache_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    if word_length < 3:
      raise MatrixDefSyntaxException("Cache improperly defined: %s; expected at least 3 tokens, got %s" % (word, word_length))
    cache_name = word[1]
    items = choices.get_regex(word[2])
    if word_length > 3:
      items = [(k, v.get(word[3])) for k, v in items]
    result = HTML_jscache % (cache_name,
                           '\n'.join(["'%s'," % ':'.join((v, k))
                                      for k, v in items]))
    return word, word_length, element, i, result


  def check_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    result = u""
    if word_length < 5:
      # TODO: Technically, before and after should be optional
      raise MatrixDefSyntaxException("Check improperly defined: %s; expected at least 5 tokens, got %s" % (word, word_length))
    vn, fn, bf, af = word[1:5]
    js = word[5] if word_length >= 6 else ''
    # TJT 2014-08-28: Adding switch here to ignore entire check definition
    # based on some other choice
    skip_this_check = False
    if word_length >= 7:
      # matrixdef contains name of choice to switch on
      switch = word[6]
      skip_this_check = self.check_choice_switch(switch, choices)
    if not skip_this_check:
      vn = prefix + vn
      checked = choices.get(vn, '') # If no choice existing, return ''
      result += html.html_input(vr, 'checkbox', vn, '', checked,
                         bf, af, onclick=js) + '\n'
    return word, word_length, element, i, result


  def file_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    if word_length < 5:
      # TODO: Technically, before and after should be optional
      raise MatrixDefSyntaxException("File improperly defined: %s; expected at least 5 tokens, got %s" % (word, word_length))
    vn, fn, bf, af = word[1:]
    vn = prefix + vn
    value = choices.get(vn, '') # If no choice existing, return ''
    result = html.html_input(vr, element.lower(), vn, value, checked=False, before=bf, after=af) + '\n'
    return word, word_length, element, i, result


  def hidden_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    if word_length < 3:
      raise MatrixDefSyntaxException("Hidden improperly defined: %s; expected at least 5 tokens, got %s" % (word, word_length))
    vn, fn = word[1:]
    value = choices.get(vn, '') # If no choice existing, return ''
    result = html.html_input(vr, element.lower(), vn, value) + '\n'
    return word, word_length, element, i, result


  def iter_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    # Syntax checking
    if word_length < 3:
      raise MatrixDefSyntaxException("BeginIter improperly defined: %s; expected at least 3 tokens, got %s" % (word, word_length))
    iter_orig = word[1]
    if "{" not in iter_orig or "}" not in iter_orig:
      raise MatrixDefSyntaxException("BeginIter improperly defined: %s; missing variable defined as {\\d}" % word)
    iter_name, iter_var = iter_orig.replace('}', '').split('{', 1)
    show_hide = 0
    if word_length > 3:
      try:
        show_hide = int(word[3])
      except ValueError as e:
        raise MatrixDefSyntaxException("BeginIter improperly defined: %s; expected 0|1, received %s" % (word, show_hide))
    iter_min = 0
    if word_length > 4:
      try:
        iter_min = int(word[4])
      except ValueError as e:
        raise MatrixDefSyntaxException("BeginIter improperly defined: %s; expected integer, received %s" % (word, iter_min))

    # Build the result
    result = u""
    label = word[2]
    # TJT 2014-08-20: adding option to only do iter based on other choice
    skip_this_iter = False
    if word_length > 5:
      # matrixdef contains name of choice to switch on
      switch = word[5]
      skip_this_iter = self.check_choice_switch(switch, choices)

    # collect the lines that are between BeginIter and EndIter
    i, section_lines = self.get_iter_lines(iter_name, i, tokenized_lines, iter_orig)

    # TJT 2014-08-20: if skipping iter, skip this whole section
    if not skip_this_iter:
      # write out the (invisible) template for the iterator
      # (this will be copied by JavaScript on the client side when
      # the user clicks the "Add" button)
      result += u'<div class="iterator" style="display: none" id="' + \
              prefix + iter_name + '_TEMPLATE">\n'
      result += html.html_delbutton(prefix + iter_name + '{' + iter_var + '}')
      result += u'<div class="iterframe">'
      result += self.defs_to_html(
                                section_lines,
                                choices,
                                vr,
                                prefix + iter_orig + '_',
                                variables
      )
      result += u'</div>\n</div>\n\n'

      # write out as many copies of the iterator as called for by
      # the current choices file OR iter_min copies, whichever is
      # greater
      c = 0
      iter_num = 0
      chlist = [x for x in choices.get(prefix + iter_name) if x]
      chlist_length = len(chlist)
      while (chlist and c < chlist_length) or c < iter_min:

        show_name = u""
        if c < chlist_length:
          iter_num = str(chlist[c].iter_num())
          show_name = chlist[c]["name"]
        else:
          iter_num = str(int(iter_num) + 1)
        new_prefix = prefix + iter_name + iter_num + '_'
        variables[iter_var] = iter_num

        # Set the variables for this iter
        # TODO: This is mutating word
        iter_lines = [replace_vars_tokenized(word, variables) for word in section_lines]

        # the show/hide button gets placed before each iterator
        # as long as it's not a stem/feature/forbid/require/lri iterator
        if show_hide:
          if show_name:
            name = show_name+" ("+new_prefix[:-1]+")"
          else:
            name = new_prefix[:-1]
          result += u'<span id="'+new_prefix[:-1]+'_errors" class="error" '
          if cookie.get(new_prefix[:-1]+'button','block') != u'none':
            result += u'style="display: none"'
          result += u'></span>'+'<a id="' + new_prefix[:-1] + 'button" ' + \
              'onclick="toggle_display_lex(\'' + \
              new_prefix[:-1] + '\',\'' + new_prefix[:-1] + 'button\')">'

          if cookie.get(new_prefix[:-1]+'button','block') == u'none':
            result += u'&#9658; '+name+'<br /></a>'
          else:
            result += u'&#9660; '+name+'</a>'

        if cookie.get(new_prefix[:-1], 'block') == u'block':
          result += u'<div class="iterator" id="' + new_prefix[:-1] + '">\n'
        else:
          result += u'<div class="iterator" style="display: none" id="' + new_prefix[:-1] + '">\n'

        result += html.html_delbutton(new_prefix[:-1])
        result += u'<div class="iterframe">'
        # TODO: Consider not doing this? Can the previous result simply be modified???
        # It looks like each iteration changes "variables"... think more about this
        # Additionally, some choices are loaded into the block via their prefix
        result += self.defs_to_html(
              iter_lines,
              choices,
              vr,
              new_prefix,
              variables
        )
        result += u'</div>\n</div>\n' # close iterator, iterframe

        del variables[iter_var]
        c += 1

      # write out the "anchor" marking the end of the iterator and
      # the "Add" button
      result += u'<div class="anchor" id="%s%s_ANCHOR"></div>\n<p>' % (prefix, iter_name)
      # add any iterator-nonspecific errors here
      result += html.validation_mark(vr, prefix + iter_name)

      # finally add the button
      result += html.html_input(vr, 'button', "", "Add %s" % label,
                                onclick="clone_region('%s', '%s', %s)" % (prefix + iter_name, iter_var, str(bool(show_hide)).lower()))

    return word, word_length, element, i, result


  def label_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    result = u""
    if word_length > 2:
      key = prefix + word[1]
      result += html.validation_mark(vr, key)
    result += word[-1] + '\n'
    return word, word_length, element, i, result


  def radio_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    if word_length < 5:
      raise MatrixDefSyntaxException("Radio button improperly defined: %s; expected at least 5 tokens, got %s: \"%s\"" % (word, word_length, " ".join([line[0] for line in tokenized_lines[i]])))
    result = u""
    vn, fn, bf, af = word[1:5]
    vn = prefix + vn
    # TJT 2014-08-28: Adding switch here to ignore entire radio definition
    # based on some other choice
    skip_this_radio = False
    if word_length >= 6:
      # matrixdef contains name of choice to switch on
      switch = word[5]
      skip_this_radio = self.check_choice_switch(switch, choices)
    # it's nicer to put vrs for radio buttons on the entire
    # collection of inputs, rather than one for each button
    if not skip_this_radio:
      mark = html.validation_mark(vr, vn)
      result += bf + mark + '\n'
      i += 1
      if i < num_lines:
        for word, word_length, element in self.__get_words(tokenized_lines[i:], variables=variables, do_replace=do_replace):
          if element != BULLET:
            break
          # Reset flags on each item
          disabled, js = u'', ''
          checked = False
          rval, rfrn, rbef, raft = word[1:5]
          # Format choice name
          if choices.get(vn) == rval: # If previously marked, mark as checked again
            checked = True
          if word_length >= 6:
            js = word[5]
          if word_length >= 7: # TJT 2014-03-19: option for disabled radio buttons
            if word[6]: # If anything here...
              disabled = True
          result += html.html_input(vr, 'radio', vn, rval, checked, rbef, raft,
                             onclick=js, disabled=disabled) + '\n'
          i += 1
      result += af + '\n'

      # Went one too far, go back one
      i -= 1
      word, word_length, element = self.__get_word(tokenized_lines, i, variables=variables, do_replace=do_replace)

    else:
      # TJT 2014-08-28: skipping radio buttons,
      # so skip the button definitions
      #while i < num_lines and tokenized_lines[i][0] == BULLET:
      while i < num_lines and tokenized_lines[i][2] == BULLET:
        i += 1

    return word, word_length, element, i, result


  def select_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    """
    Given the parameters, generate the html for a Select element

    This method sets the "temp" value of the currently selected option, sending
    the proper information to the JavaScript method on the client side.
    The "temp" class signals that the option be removed prior to interacting with
    the select element
    """
    result = u""
    multi = element == MULTI_SELECT
    vn, fn, bf, af = word[1:5]

    onfocus, onchange = u'', u''
    if word_length > 5: onfocus = word[5]
    if word_length > 6: onchange = word[6]

    vn = prefix + vn

    result += bf + '\n'

    fillers = []

    # look ahead and see if we have an auto-filled drop-down
    i += 1
    while i < num_lines:
      word, word_length, element = self.__get_word(tokenized_lines, i, variables=variables, do_replace=do_replace)
      # TODO: Consider if the fill commands could go anywhere in the list...
      if element.startswith('fill'):
        # arguments are labeled like p=pattern, l(literal_feature)=1,
        # n(nameOnly)=1, c=cat
        argstring = u','.join(['true' if a in ('n', 'l') else "'%s'" % x
                              for a, x in [w.split('=') for w in word[1:]]])
        fillers.append(self.fillstrings[element] % {'args':argstring})
        i += 1
      else:
        break

    if fillers:
      fillcmd = u"fill('%s', [].concat(%s));" % (vn, ','.join(fillers))
      onfocus = fillcmd + onfocus

    # Build the select element
    result += html.html_select(vr, vn, multi, onfocus=onfocus, onchange=onchange) + '\n'

    # Add individual bullets, if applicable
    printed_selected = False
    sval = choices.get(vn)
    if i < num_lines:
      for word, word_length, element in self.__get_words(tokenized_lines[i:], variables=variables, do_replace=do_replace):
        if element == BULLET:
          sstrike = False # Reset variable
          # select/multiselect options
          oval, ofrn, ohtml = word[1:4]
          # TJT 2014-03-19: add disabled option to allow for always-disabled option
          # If there's anything in this slot, disable option
          if word_length >= 5: sstrike = True
          result += html.html_option(vr, oval, sval == oval, ofrn, strike=sstrike) + '\n'
          if sval == oval:
            printed_selected = True
          i += 1
        else:
          break

    # Get previously selected item
    # This is necessary because the value is not in the deffile
    if sval and not printed_selected:
      # This needs to be temp=True (the client side code uses this value and then deletes it)
      result += html.html_option(vr, sval, True, self.f(sval), temp=True) + '\n'

    # add empty option
    result += html.html_option(vr, '', False, '') + '\n'
    result += u'</select>'
    result += af + '\n'

    # Went one too far, go back one
    i -= 1
    word, word_length, element = self.__get_word(tokenized_lines, i, variables=variables, do_replace=do_replace)

    return word, word_length, element, i, result


  def separator_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    return word, word_length, element, i, u"<hr>\n"


  def text_to_html(self, tokenized_lines, choices, vr, cookie, prefix, variables, num_lines, word, word_length, element, i, do_replace=False):
    result = u""
    vn, fn, bf, af, sz = word[1:6]
    oc = word[6] if word_length > 6 else u''
    # TJT 2014-08-27: Prepend auto onchange events (instead of assinging)
    if vn == u"name":
      oc = u"fill_display_name('"+prefix[:-1]+"');" + oc
    # TJT 2014-08-26: Adding auto check radio button
    # on morphology page affixes
    elif vn == u"orth":
      # If previous non-empty line a radio definition, add check radio
      # button function to onChange (for affixes)
      if tokenized_lines[i-1][2] == BULLET:
        oc = u"check_radio_button('"+prefix[:-1]+"_inflecting', 'yes'); " + oc
    vn = prefix + vn
    value = choices.get(vn, u'')

    result += html.html_input(vr, element.lower(), vn, value,
                checked=False, before=bf, after=af, size=sz, onchange=oc)
    result += u"\n"

    return word, word_length, element, i, result


  ##############################################################################
  # Helpers

  def get_iter_lines(self, iter_name, i, tokenized_lines, iter_orig):
    i += 1
    section_lines = []
    for word, word_length, element in tokenized_lines[i:]:
      if word_length and element == END_ITER and word[1] == iter_name:
        break
      section_lines.append((word, word_length, element))
      i += 1
    else:
      raise MatrixDefSyntaxException("Missing EndIter statement for Iter \"%s\"" % iter_orig)

    return i, section_lines


  def get_cookie(self, http_cookie=os.getenv(HTTP_COOKIE)):
    result = {}
    if http_cookie:
      for c in http_cookie.split(';'):
        name, value = c.split('=', 1)
        result[name.strip()] = value
    return result


  def __get_word(self, tokenized_lines, i, variables={}, do_replace=False):
    """
    Get a line from tokenized_lines, returning the metadata about the line and doing variable replacement if specified
    NOTE: This method isn't needed to simply accessing tokenized_lines,
          but provides a consistent way of doing variable replacements
    """
    word, word_length, element = tokenized_lines[i]
    return self.__do_get(word, word_length, element, variables=variables, do_replace=do_replace)


  def __get_words(self, tokenized_lines, variables={}, do_replace=False):
    """
    Iterate through lines of tokenized_lines, returning the metadata about each line and doing variable replacement if specified
    NOTE: This method isn't needed to simply accessing tokenized_lines,
          but provides a consistent way of doing variable replacements
    """
    for word, word_length, element in tokenized_lines:
      yield self.__do_get(word, word_length, element, variables=variables, do_replace=do_replace)


  def __do_get(self, word, word_length, element, variables={}, do_replace=False):
    """
    see __get_word(), __get_words()
    """
    if do_replace and variables:
      word = replace_vars_tokenized(word, variables)
    return word, word_length, element


  ##############################################################################
  # Choice saving methods

  def save_choices(self, form_data, choices_file):
    """
    Save the given form_data to the specified choices file
    """
    section = form_data['section'].value
    current_page_choices = self.load_choices_from_form(form_data)
    other_page_choices = ChoicesFile(choices_file)

    # Add additional choices based on new choices
    self.enhance_choices(section, current_page_choices, other_page_choices)

    # Save the choices to file
    with codecs.open(choices_file, 'w', encoding="utf-8") as f:
      f.write(u'\n') # blank line in case an editor inserts a BOM
      f.write(u'version=%d\n\n' % other_page_choices.current_version())

      for section_name in self.sections:
        choices = current_page_choices if section_name == section else other_page_choices
        f.write(u'section=%s\n' % section_name)
        self.save_choices_section(self.sections[section_name], f, choices)
        f.write(u'\n')


  def enhance_choices(self, section, current_page_choices, other_page_choices):
    """
    Given new choices from the user, alter the existing choices (via mutation)
    For instance, if a user specifies a choice on a library subpage, add a corresponding
      choice to the morphology subpage
    """
    if section in ('lexicon', 'morphology'):
      if section == u'lexicon':
        self.create_optcop_pc_choices(current_page_choices, other_page_choices)
        feats_to_add = self.get_lexical_adj_arg_agreement_feats_to_add(current_page_choices, other_page_choices)

      else: # if section == u'morphology':
        feats_to_add = self.get_morphological_adj_arg_agreement_feats_to_add(current_page_choices, other_page_choices)

      self.create_adj_arg_agreement_pc_choices(feats_to_add, section, current_page_choices, other_page_choices)


    if section == u'sentential-negation':
      # TODO: Write unit tests for these
      # TODO: These methods are mutating their input; they should not also return their input
      # if neg-aux=on exists, create side-effect in lexicon.
      if (current_page_choices.get('neg-aux', '') or (current_page_choices.get('bineg-type', '') == 'infl-head')):
        # see if we're already storing an index number
        neg_aux_index = other_page_choices.get('neg-aux-index', '')
        if neg_aux_index:
          # we have an index for a neg-aux, see if it's still around
          if not other_page_choices['aux%s' % neg_aux_index]:
            # it's not so we make a new neg-aux and store the index
            other_page_choices, neg_aux_index = self.create_neg_aux_choices(other_page_choices)
            current_page_choices["neg-aux-index"] = unicode(neg_aux_index) if neg_aux_index > 0 else u'1'
        else: # we don't have any neg aux index stored, so make a new one
          other_page_choices, neg_aux_index = self.create_neg_aux_choices(other_page_choices, current_page_choices)
          current_page_choices["neg-aux-index"] = unicode(neg_aux_index) if neg_aux_index > 0 else u'1'


      # create a zero-neg lri in choices
      if current_page_choices.get('neg-exp', '') == u'0' and current_page_choices.get('vpc-0-neg', ''):
        # infl-neg should be on for zero-neg to work
        current_page_choices['infl-neg'] = u'on'
        other_page_choices, current_page_choices = self.create_infl_neg_choices(other_page_choices, current_page_choices)


      # add FORM subtype for neg1b-neg2b analysis
      # also add it for infl-head neg analysis
      # TODO: Functionalize this
      neg1_type = current_page_choices.get('neg1-type', '')
      neg2_type = current_page_choices.get('neg2-type', '')
      if current_page_choices.get('neg1b-neg2b', '') or \
         (neg1_type == 'fh' and neg2_type == 'b') or \
         (neg2_type == 'fh' and neg1_type == 'b'):
        next_n = other_page_choices['nf-subform'].next_iter_num() if 'nf-subform' in other_page_choices else 1
        if next_n > 1:
          nfss = other_page_choices.get('nf-subform')
          for nfs in nfss:
            if nfs['name'] == u'negform':
              break
          else:
            other_page_choices['nf-subform%d_name' % next_n] = u'negform'


  def load_choices_from_form(self, form_data):
    """
    Load new choices from form_data
    """
    result = ChoicesFile('')
    for k in (k for k in form_data.keys() if k):
      # Some choices are hidden in more than one place, so the FieldStorage
      # object at [k] can be a list, but in these cases only one item on the
      # list should ever have a value
      if isinstance(form_data[k], list):
        for l in form_data[k]:
          if l.value:
            val = l.value
            if isinstance(val, str):
              val = unicode(val, 'utf-8')
            result[k] = val
            break
      else:
        val = form_data[k].value
        if isinstance(val, str):
          val = unicode(val, 'utf-8')
        result[k] = val
    return result


  CHOICES_TO_SAVE = {CHECK, TEXT, TEXT_AREA, RADIO, SELECT, MULTI_SELECT, FILE, HIDDEN}

  def save_choices_section(self, tokenized_lines, f, choices,
                           iter_level=0, prefix=u''):
    """
    Based on a section of a matrix definition file in tokenized_lines, save the
    values from choices into the file handle f. The section in tokenized_lines
    need not correspond to a whole named section (e.g. "Lexicon"), but
    can be any part of the file not containing a section line.

    # TODO: Move this to choices.py
    """
    saved = set()
    i = 0
    while i < len(tokenized_lines):
      word, word_length, element = tokenized_lines[i]
      if element in self.CHOICES_TO_SAVE:
        vn = word[1]
        name = prefix + vn
        if vn and name not in saved:
          saved.add(name)
          # TODO: this choice is being returned as a str
          val = choices.get(name, False)
          if val:
            if element == TEXT_AREA:
              val = u'\\n'.join(val.splitlines())
            f.write(u'  '*iter_level)
            f.write(prefix + vn + u'=' + val + u'\n')

      elif element == BEGIN_ITER:
        # Recurse
        iter_name, iter_var = word[1].replace(u'}', u'').split(u'{', 1)
        i, section_lines = self.get_iter_lines(iter_name, i, tokenized_lines, word[1])

        name = prefix + iter_name
        for var in choices.get(name):
          self.save_choices_section(
            section_lines,
            f,
            choices,
            iter_level=iter_level+1,
            prefix="".join((name, unicode(var.iter_num()), '_')))

      i += 1


  ##############################################################################
  # Methods to add choices on save
  def create_optcop_pc_choices(self, current_page_choices, other_page_choices):
    """
    # If optionally copula complement, add zero rules to morphology page
    # This method expects to be running from the lexicon section
    """
    for adj in current_page_choices.get('adj', []):
      if adj.get(u'predcop') == u"opt":
        atype = get_name(adj)
        pc_name = u"%s_opt_cop" % atype
        # Skip if already added
        if not any(pc.get('name','') == pc_name for pc in other_page_choices['adj-pc']):
          switching_pc = u"adj-pc%d" % (other_page_choices['adj-pc'].next_iter_num()
                                        if other_page_choices['adj-pc'] else 1)

          # TODO: Set section to morphology; This would require some significant restructuring

          # Set up position class
          other_page_choices[switching_pc+u"_name"] = pc_name
          other_page_choices[switching_pc+u"_obligatory"] = u"on"
          other_page_choices[switching_pc+u"_inputs"] = atype
          # Set up new position class as a "switching" pc
          other_page_choices[switching_pc+u'_switching'] = u"on"

          # Define lexical rule types
          aToA = switching_pc+u'_lrt1'
          aToV = switching_pc+u'_lrt2'
          # Write adjective to adjective rule
          other_page_choices[aToA+u"_name"] = u"%s_cop_comp" % atype
          other_page_choices[aToA+u"_predcop"] = u"on"
          other_page_choices[aToA+u"_mod"] = u"pred"
          # Write adjective to verb rule
          other_page_choices[aToV+u"_name"] = u"%s_stative_pred" % atype
          other_page_choices[aToV+u"_mod"] = u"pred"


  def get_lexical_adj_arg_agreement_feats_to_add(self, current_page_choices, other_page_choices):
    """
    Gather features for adjective lexical items that agree with only one argument
    """
    result = defaultdict(list)

    for adj in current_page_choices.get(u'adj', []):
      for feat in adj.get(u'feat', []):
        if feat.get(u'head',u'') in (u'subj',u'mod'):
          atype = get_name(adj)
          pc_name = u"%s_argument_agreement" % atype
          # Skip if already added
          if not any(pc.get(u'name',u'') == pc_name for pc in other_page_choices[u'adj-pc']):
            result[atype].append(feat)
    return result


  def get_morphological_adj_arg_agreement_feats_to_add(self, current_page_choices, other_page_choices):
    """
    Gather features for adjective morphological rules that agree with only one argument
    """
    result = defaultdict(list)

    for adj_pc in current_page_choices.get('adj-pc', []):
      for lrt in adj_pc.get('lrt', []):
        for feat in lrt.get('feat', []):
          if feat.get('head','') in ('subj','mod'):
            apc = adj_pc.full_key
            pc_name = u"%s_argument_agreement" % apc
            # Skip if already added
            if not any(pc.get('name','') == pc_name for pc in other_page_choices['adj-pc']):
              result[apc].append(feat)
    return result


  def create_adj_arg_agreement_pc_choices(self, feats_to_add, section, current_page_choices, other_page_choices):
    """
    Add zero rules to choices for lexical items and morphological rules that agree with only
    one argument of the adjective
    """
    target_page_choices = other_page_choices if section == u"lexicon" else current_page_choices
    for adj in feats_to_add:
      # Add zero rules
      argument_agreement_pc = u"adj-pc%d" % (target_page_choices['adj-pc'].next_iter_num()
                                             if target_page_choices['adj-pc'] else 1)
      # Set up position class
      # TODO: Make the name use the friendly name
      target_page_choices[argument_agreement_pc+u'_name'] = u"%s_argument_agreement" % adj
      target_page_choices[argument_agreement_pc+u'_obligatory'] = u'on'
      target_page_choices[argument_agreement_pc+u'_inputs'] = adj
      # Set up new position class as a "switching" pc
      target_page_choices[argument_agreement_pc+u'_switching'] = u'on'
      # Define lexical rule types
      subj_only = argument_agreement_pc+u'_lrt1'
      mod_only = argument_agreement_pc+u'_lrt2'
      # Write subject agreement rule
      target_page_choices[subj_only+u'_name'] = u"%s_subj_agr" % adj
      target_page_choices[subj_only+u'_mod'] = u'pred'
      # Write modificand agreement rule
      target_page_choices[mod_only+u"_name"] = u"%s_mod_agr" % adj
      target_page_choices[mod_only+u"_mod"] = u"attr"
      # Add features from lexicon page to morphology page
      feat_count = 1
      for feat in feats_to_add[adj]:
        head = feat.get('head','').lower()
        if head in ('subj', 'mod'):
          if head == u'subj':
            # Copy subject agreement features
            feature_vn = subj_only+u"_feat%d" % feat_count
          elif head == u'mod':
            # Copy object agreement features
            feature_vn = mod_only+u"_feat%d" % feat_count
          target_page_choices[feature_vn+u'_name'] = feat.get('name')
          target_page_choices[feature_vn+u'_value'] = feat.get('value')
          # Adjectives' MOD, XARG, and SUBJ identified
          # so just agree with the XARG (since the syntax is constrained)
          target_page_choices[feature_vn+u'_head'] = u'xarg'
          # Delete this feature from current page
          current_page_choices.delete(feat.full_key+u'_name')
          current_page_choices.delete(feat.full_key+u'_value')
          current_page_choices.delete(feat.full_key+u'_head', prune=True)
          feat_count += 1


  def create_neg_aux_choices(self, other_page_choices, current_page_choices):
    """
    this is a side effect of the existence of neg-aux
    in the form data, it puts some lines pertaining to a neg-aux
    lexical item into the choices file object unless they are
    already there. returns a ChoicesFile instance, and an int
    which is the index number of the created neg-aux

    TODO: Move this to choices.py
    """

    # get the next aux number
    next_n = other_page_choices['aux'].next_iter_num() if 'aux' in other_page_choices else 1

    # create a new aux with that number
    other_page_choices['aux%d_name' % next_n] = u'neg'

    # copy that to nli for adding further information
    nli = other_page_choices['aux'].get_last()
    nli['sem'] = 'add-pred'
    nli['stem1_pred'] = u'neg_rel'

    if other_page_choices.get('bineg-type', '') == 'infl-head':
      nli['compfeature1_name'] = 'form'
      nli['compfeature1_value'] = 'negform'

    # if auxiliaries are off, turn them on
    choices['has-aux'] = u'yes'
    return choices, next_n


  def create_infl_neg_choices(self, old_choices, new_choices):
    """
    TODO: Move this to choices.py
    """
    vpc = new_choices['vpc-0-neg']
    lrt = u''
    if vpc == u'create':
      next_n = old_choices['verb-pc'].next_iter_num() if old_choices['verb-pc'] else 1
      old_choices['verb-pc%d_name' % next_n] = u'negpc'
      vpc = old_choices['verb-pc'].get_last()
      vpc['lrt1_name'] = u'neg'
      lrt = old_choices['verb-pc'].get_last()['lrt'].get_last()
      new_choices['vpc-0-neg'] = u'verb-pc'+str(next_n)

    else:
      next_n = old_choices[vpc]['lrt'].next_iter_num() if old_choices[vpc]['lrt'] else 1
      # create new lrt in this position class
      old_choices[vpc]['lrt%d_name' % next_n] = u'neg'
      # add some features for negation and empty PHON
      lrt = old_choices[vpc]['lrt'].get_last()

    lrt['feat1_name']= u'negation'
    lrt['feat1_value'] = u'plus'
    lrt['feat1_head'] = u'verb'
    lrt['lri1_inflecting'] = u'no'
    return old_choices, new_choices


class MatrixDefSyntaxException(Exception):
    """
    A syntax exception encountered during the parsing of the matrixdef file
    """
    pass


def exception_html(exc):
  if exc and exc != (None, None, None):
    print '<p style="text-align:center">You may also wish to ' +\
          '<a href="#" onclick="toggle_visible(\'error\');">' +\
            'see the Python error</a> ' +\
          '(note: it is very technical, and possibly not useful).</p>'
    print "<div id=\"error\" style=\"display:none\">"
    cgitb.handler(exc)
    print "</div>"
