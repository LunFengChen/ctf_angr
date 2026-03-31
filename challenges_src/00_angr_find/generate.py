#!/usr/bin/env python3
import sys, random, os, tempfile, jinja2

def generate(seed):

  random.seed(seed)
  userdef_charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  userdef = ''.join(random.choice(userdef_charset) for _ in range(8))

  template = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '00_angr_find.c.jinja'), 'r').read()
  t = jinja2.Template(template)
  c_code = t.render(userdef=userdef, len_userdef=len(userdef), description = '')

  return {
    'c_code': c_code,
    'flags': ['-fno-pie', '-no-pie', '-fcf-protection=none']
  }

if __name__ == '__main__':
    print("Refactored, call from build.py")
