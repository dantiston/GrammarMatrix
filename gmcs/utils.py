#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

### $Id: utils.py,v 1.8 2008-05-28 21:08:12 sfd Exp $


def make_tgz(directory):
  # ERB First get rid of existing file because gzip won't
  # overwrite existing .tgz meaning you can only customize
  # grammar once per session.
  if os.path.exists('matrix.tar.gz'):
    os.remove('matrix.tar.gz')

  archive = directory + '.tar'
  with tarfile.open(archive, 'w') as t:
    t.add(directory)

  with gzip.open(archive + '.gz', 'wb') as g:
    with open(archive, 'rb') as f:
      g.write(f.read())

  os.remove(archive)


def add_zip_files(z, directory):
  files = os.listdir(directory)
  for f in files:
    cur = os.path.join(directory, f)
    if os.path.isdir(cur):
      add_zip_files(z, cur)
    else:
      z.write(cur, cur)


def make_zip(directory):
  with zipfile.ZipFile(directory + '.zip', 'w') as z:
    add_zip_files(z, directory)


def TDLencode(string):
  """
  Encode a string in such a way as to make it a legal TDL type name
  """
  val = ''
  for c in string:
    if not (c.isalnum() or ord(c) > 127 or c in (u'_', u'-', u'+', u'*')):
      val += u'%' + u'%2X' % (ord(c))
    else:
      val += c

  return val


def orth_encode(orthin):
  """
  prepare an orth string in a way that
  words with spaces are treated properly.
  """
  orthlist = orthin.split(u' ')
  orthout = u''
  if len(orthlist) > 1:
    orthout = u'","'.join(orthlist)
  else:
    orthout = orthlist[0]
  return orthout


def get_name(item):
  return item.get('name', None) or item.full_key


def format_comment_block(comment_string, max_chars=70, prefix=';;;'):
  lines = []
  comment_lines = comment_string.split('\\n')
  for s in comment_lines:
    lines += [prefix]
    toks = s.split(' ')
    for tok in toks:
        if len(lines[-1]) + len(tok) > max_chars:
            lines += [prefix + ' ' + tok]
        else:
            lines[-1] += ' ' + tok
  return '\n'.join(lines)


def verify():
  return raw_input("  Do you want to continue? (y/n): ").lower() in ('y','yes')
