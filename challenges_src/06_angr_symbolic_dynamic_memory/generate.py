#!/usr/bin/env python3
import sys, random, os, tempfile, jinja2

def generate(seed):
  random.seed(seed)
  userdef_charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  userdef0 = ''.join([random.choice(userdef_charset) for _ in range(8)])
  userdef1 = ''.join([random.choice(userdef_charset) for _ in range(8)])
  padding = random.randint(0, 2**26)

  template = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '06_angr_symbolic_dynamic_memory.c.jinja'), 'r').read()
  t = jinja2.Template(template)
  c_code = t.render(description='', padding=padding, userdef0=userdef0, userdef1=userdef1)

  return {
    'c_code': c_code,
    'flags': ['-fno-pie', '-no-pie']
  }

if __name__ == '__main__':
  print("Refactored, call from build.py")
