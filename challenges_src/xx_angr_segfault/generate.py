#!/usr/bin/env python3

import sys, random, os, tempfile, jinja2

def expanded_switch_statement(variable, miss_statement, hit_statement, samples):
  target = random.choice(samples)

  ret_str = 'switch (%s) {' % (variable,)
  for sample in samples:
    ret_str += 'case %d: %s; break;' % (sample, hit_statement if sample == target else miss_statement)
  ret_str += 'default: %s; break; }' % (miss_statement,)
  return ret_str

def generate(seed):

  random.seed(seed)
  
  description = ''
  desc_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'description.txt')
  if os.path.exists(desc_path):
      with open(desc_path, 'r') as desc_file:
          description = desc_file.read().encode('unicode_escape').decode('utf-8')

  hit_statement = 'locals.random_char = *(&locals.allocated_memory);'
  miss_statement = 'locals.random_char = *locals.arbitrary_pointer;'
  expanded_switch_statement_string = expanded_switch_statement('key', miss_statement, hit_statement, random.sample(range(2**26-1), 2))

  template = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'xx_angr_segfault.c.jinja'), 'r').read()
  c_code = jinja2.Template(template).render(description=description, expanded_switch_statement=expanded_switch_statement_string)

  return {
    'c_code': c_code,
    'flags': ['-fno-pie', '-no-pie', '-fno-stack-protector']
  }

if __name__ == '__main__':
  print("Refactored, call from build.py")
