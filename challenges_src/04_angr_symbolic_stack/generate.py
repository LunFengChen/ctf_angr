#!/usr/bin/env python3
import sys, random, os, tempfile, jinja2

def generate(seed):
  random.seed(seed)

  userdef0 = random.randint(0, 0xFFFFFFFF)
  userdef1 = random.randint(0, 0xFFFFFFFF)
  complex_function0_string = ''.join([ (f'value ^= {random.randint(0,0xFFFFFFFF)};') for _ in range(32) ])
  complex_function1_string = ''.join([ (f'value ^= {random.randint(0,0xFFFFFFFF)};') for _ in range(32) ])

  template = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '04_angr_symbolic_stack.c.jinja'), 'r').read()
  t = jinja2.Template(template)
  c_code = t.render(description = '', complex_function0=complex_function0_string, complex_function1=complex_function1_string, userdef0=userdef0, userdef1=userdef1)

  return {
    'c_code': c_code,
    'flags': ['-fno-stack-protector', '-fno-pie', '-no-pie']
  }

if __name__ == '__main__':
  print("Refactored, call from build.py")


