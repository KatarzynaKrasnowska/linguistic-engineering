#!/usr/bin/env python:e
# -*- coding: utf-8 -*-

import codecs
import re
import itertools

from tags import TAGS

abbrs = set()
dot_abbrs = set()

def abbreviation(tokens, i):
  if not abbrs:
    with codecs.open('skroty.txt', encoding='utf_8', mode='r') as f:
      for abbr, _ in (l.split('\t') for l in f.readlines()):
        if abbr.endswith('.'):
          dot_abbrs.add(abbr[:-1])
        else:
          abbrs.add(abbr)
  if tokens[i].endswith('.'):
    if tokens[i][:-1] in dot_abbrs:
      return [(tokens[i][:-1], TAGS.ABBR), ('.', TAGS.INTERP)]
  elif tokens[i] in abbrs:
    return [(tokens[i], TAGS.ABBR)]

months = {
    u'styczeń' : TAGS.M_I, u'stycznia' : TAGS.M_I,
    u'luty' : TAGS.M_II, u'lutego' : TAGS.M_II,
    u'marzec' : TAGS.M_III, u'marca' : TAGS.M_III,
    u'kwiecień' : TAGS.M_IV, u'kwietnia' : TAGS.M_IV,
    u'maj' : TAGS.M_V, u'maja' : TAGS.M_V,
    u'czerwiec' : TAGS.M_VI, u'czerwca' : TAGS.M_VI,
    u'lipiec' : TAGS.M_VII, u'lipca' : TAGS.M_VII,
    u'sierpień' : TAGS.M_VIII, u'sierpnia' : TAGS.M_VIII,
    u'wrzesień' : TAGS.M_IX, u'września' : TAGS.M_IX,
    u'październik' : TAGS.M_X, u'października' : TAGS.M_X,
    u'listopad' : TAGS.M_XI, u'listopada' : TAGS.M_XI,
    u'grudzień' : TAGS.M_XII, u'grudnia' : TAGS.M_XII,
}

# Right now assign a month token to whatever may be a month.
def month(tokens, i):
  if tokens[i] in months:
    return [(tokens[i], months[tokens[i]])]

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
      return [(tokens[i], ABBR)]
    else:
      subtokens = [token.strip() for token in re.split('(\.)$', tokens[i], re.UNICODE)]
      tags = itertools.chain.from_iterable(
               (assign_tag(subtokens, i) for i, token in enumerate(subtokens) if token))
      return tags

def unknown_token(tokens, i):
  return [(tokens[i], TAGS.UNKNOWN)]

SIMPLE_TAG_FILTERS = [
    regexp_based_tag(r'^([0-9]+(,[0-9]+)?)$', TAGS.ARA),
    regexp_based_tag(r'^(([ivxlcdm]+)|([IVXLCDM]+))$', TAGS.ROM), # OK, this is not neccesarly roman number :)
    regexp_based_tag(r'^([0-9]{0,2}[\-\.\/]((0?[1-9])|(1[0-2]))[\-\.\/][1-9][0-9]{1,3})$', TAGS.DATE),
    month,
    regexp_based_tag(r'^(\w+)$', TAGS.WORD),
    regexp_based_tag(r'^([\,\:\;\.\-\?\!\(\)])$', TAGS.INTERP),
    #regexp_based_tag(r'^(\w{1,3}\.)$', 'ABBR'),
    # Copy pasted regexp for url from: http://stackoverflow.com/questions/833469/regular-expression-for-url
    abbreviation,
    word_with_dot,
    regexp_based_tag(r'^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*$', TAGS.WWW),
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
