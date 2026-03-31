#!/usr/bin/env python3
import sys, random, os, tempfile, jinja2

def generate(seed):
  random.seed(seed)

  userdef_charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  userdef = ''.join(random.choice(userdef_charset) for _ in range(8))

  template = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '14_angr_shared_library_so.c.jinja'), 'r').read()
  t = jinja2.Template(template)
  c_code = t.render(description='', userdef=userdef, len_userdef=len(userdef))

  pass

  shared_c_code = t.render(description='', userdef=userdef, len_userdef=len(userdef))
  main_c_code = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '14_angr_shared_library.c'), 'r').read()
  return {
    'c_code': main_c_code,
    'shared_c_code': shared_c_code,
    'flags': ['-fno-pie', '-no-pie']
  }
