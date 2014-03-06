#!/usr/bin/env python:e
# -*- coding: utf-8 -*-

import re
import itertools

def regexp_based_tag(regex, tag):
  def matcher(tokens, i):
    match = re.match(regex, tokens[i], re.UNICODE)
    if match is not None:
      return [(tokens[i], tag)]
  return matcher

def comma_separated_tokens(tokens, i):
  if ',' in tokens[i]:
    subtokens = [token.strip() for token in re.split('(\,)', tokens[i], re.UNICODE)]
    tags = itertools.chain.from_iterable(assign_tag(subtokens, i) for i, token in enumerate(subtokens) if token)
    return tags

def word_with_dot(tokens, i):
  if tokens[i].endswith('.'):
    if i < len(tokens) - 1:
      return [(tokens[i], 'ABBR')]
    else:
      subtokens = [token.strip() for token in re.split('(\.)', tokens[i], re.UNICODE)]
      tags = itertools.chain.from_iterable(
               (assign_tag(subtokens, i) for i, token in enumerate(subtokens) if token))
      return tags

def unknown_token(tokens, i):
  return [(tokens[i], 'UNKNOWN')]

SIMPLE_TAG_FILTERS = [
    regexp_based_tag(r'^([0-9]+(,[0-9]+)?)$', 'ARABIC'),
    regexp_based_tag(r'^(([ivxlcdm]+)|([IVXLCDM]+))$', 'ROMAN'), # OK, this is not neccesarly roman number :)
    regexp_based_tag(r'^([0-9]{0,2}[\-\.\/]((0?[1-9])|(1[0-2]))[\-\.\/][1-9][0-9]{1,3})$', 'DATE'),
    regexp_based_tag(r'^(\w+)$', 'TEXT'),
    regexp_based_tag(r'^([\,\;\.\-\?\!])$', 'INTERP'),
    regexp_based_tag(r'^(\w{1,3}\.)$', 'ABBR'),
    # Copy pasted regexp for url from: http://stackoverflow.com/questions/833469/regular-expression-for-url
    regexp_based_tag(r'^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*$', 'URL'),
    word_with_dot,
    comma_separated_tokens,
    unknown_token,
]


def assign_tags(tokens):
  return itertools.chain.from_iterable(assign_tag(tokens, i) for i, token in enumerate(tokens))

def assign_tag(tokens, i):
  for fn in SIMPLE_TAG_FILTERS:
    tag = fn(tokens, i)
    if tag is not None:
      return tag

print list(assign_tags('Ala ma 13 lat, bo urodzila się w 17.01.1988 r.'.decode('utf-8').split(' ')))
print " "
print list(assign_tags('W XXI w. urle są takie http://www.mimuw.edu.pl'.decode('utf-8').split(' ')))
print " "
tests = [
   '05.03.2014',
   '5.3.2014',
   '05/03/2014',
   '5/3/2014',
   '5 marca 2014',
   '5 marca 2014 r.',
   '5 III 2014',
   ]
for test in tests:
  print test, list(assign_tags(test.split(' ')))
  print " "
