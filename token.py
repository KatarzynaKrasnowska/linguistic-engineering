#!/usr/bin/env python:e
# -*- coding: utf-8 -*-

import codecs
import re
import itertools

from tags import TAGS

def ara_with_dot(tokens, i):
  match = re.match(r'^([0-9]+\.)$', tokens[i], re.UNICODE)
  if match is not None:
    return [(tokens[i][:-1], TAGS.ARA), (u'.', TAGS.INTERP)]
  # 03.2014 - treat as ara-punct-ara
  match = re.match(r'^([0-9]+)\.([0-9]+)$', tokens[i], re.UNICODE)
  if match is not None:
    return [(match.group(1), TAGS.ARA), (u'.', TAGS.INTERP), (match.group(2), TAGS.ARA)]


# Sentences starting with [WAUZO] (W czym, A co, U kogo, Z kim, O czym)
def first_conj(tokens, i):
  if i == 0 and tokens[i] in (u'W', u'A', u'U', u'Z', u'O'):
    return [(tokens[i], TAGS.WORD)]

def conjunction_i(tokens, i):
  if i == 0 and tokens[i] == u'I':
    return [(tokens[i], TAGS.WORD)]
  if tokens[i] == u'i':
    return [(tokens[i], TAGS.WORD)]

def name_abbrev(word):
  upper = False # there are capital letters in name
  if len(word) > 1: # we assume no 1 letter abbreviations here
    if word[0].isupper():
      for position in range(1,len(word)-1):
        curr = word[position]
        prev = word[position -1]
        if curr.isupper() and not prev == u'-':
          upper = True
  return upper
    

unit_names = set()
unit_prefixes = set()
units = set()
abbrs = set()
dot_abbrs = set()
abbrs_all = set()
def abbreviation(tokens, i):
  global dot_abbrs, abbrs_all, unit_names, unit_prefixes, units, abbrs
  if not abbrs:
    # known dot abbreviations that can end sentence
    with codecs.open('dots_sorted.txt', encoding='utf_8', mode='r') as f:
      for abbr in f.readlines():
        dot_abbrs.add(abbr.strip()[:-1])
    # ceating possible names of physical units
    with codecs.open('unit_names.txt', encoding='utf_8', mode='r') as f:
      for name in f.readlines():
        unit_names.add(name.strip()) # a (Are) is not included in file due to collisions
    with codecs.open('unit_prefixes.txt', encoding='utf_8', mode='r') as f:
      for prefix in f.readlines():
        unit_prefixes.add(prefix.strip())
    for name in unit_names:
      units.add(name)
      for prefix in unit_prefixes:
        units.add(prefix + name) # some nonsense may be added (like kha) but no polish word should be generated
    # no-dot abbreviations
    with codecs.open('uninflected.txt', encoding='utf_8', mode='r') as f:
      for abbr in f.readlines():
        abbrs.add(abbr.strip())
    with codecs.open('inflected.txt', encoding='utf_8', mode='r') as f:
      for abbr in f.readlines():
        abbrs.add(abbr.strip()) # @TODO: add some inflation in way similar to units
    # union of all abbreviations
    abbrs_all = abbrs.union(dot_abbrs).union(units)

  if tokens[i].endswith('.') and len(tokens[i]) > 1: # tokens ends with dot
    t = tokens[i][:-1]
    # TODO: assuming roman numerals will be interpreped later and re-tagged
    if i + 1 < len(tokens): # this is not sentence-ending dot
      return [(t, TAGS.ABBR), ('.', TAGS.INTERP)]
    else: # this is sentence-endig dot
      if t in abbrs_all or (len(t) == 1 and t.isupper()): # known abbreviation or name initial
        return [(t, TAGS.ABBR), ('.', TAGS.INTERP)]
  elif tokens[i] in abbrs.union(units):
    return [(tokens[i], TAGS.ABBR)]
  elif name_abbrev(tokens[i]): # PZPR, PKiN, etc.; may lead to problems with fully capitalized words or roman numerals
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

def hyphen_separated_tokens(tokens, i):
  hyphen_regex = ur'(.*?)([%s\-])(.*)$' % interp_hyphens
  subtokens = []
  token = tokens[i]
  m = re.match(hyphen_regex, tokens[i], re.UNICODE)
  while m:
    t1, hyph, token = m.group(1,2,3)
    subtokens += [t1, hyph]
    m = re.match(hyphen_regex, token, re.UNICODE)
  subtokens.append(token)
  if len(subtokens) > 1:
    tags = itertools.chain.from_iterable(assign_tag(subtokens, i) for i, token in enumerate(subtokens) if token)
    return tags

def word_with_dot(tokens, i):
  if tokens[i].endswith('.'):
    if i < len(tokens) - 1:
      return [(tokens[i], TAGS.ABBR)]
    else:
      subtokens = [token.strip() for token in re.split('(\.)$', tokens[i], re.UNICODE)]
      tags = itertools.chain.from_iterable(
               (assign_tag(subtokens, i) for i, token in enumerate(subtokens) if token))
      return tags

def unknown_token(tokens, i):
  return [(tokens[i], TAGS.UNKNOWN)]

interp_hyphens = u'\u2010\u2011\u2012\u2013\u2014\u2015'
# the last sign here is a triple dot :)
interp_quotes = u'\'"`\u2018\u201A\u201B\u201C\u201D\u201E\u201F\u2026'
interp_not_dot = interp_hyphens + interp_quotes + u',:;-?!()[]'
interp_regex = ur'[%s%s\,\:\;\.\-\?\!\(\)\[\]]' % (interp_hyphens, interp_quotes)

SIMPLE_TAG_FILTERS = [
    regexp_based_tag(r'^([0-9]+)$', TAGS.INT),
    regexp_based_tag(r'^([0-9]+,[0-9]+)$', TAGS.ARA),
    ara_with_dot,
    # "i" and "I" at the beginning of a sentence are not roman numbers :)
    conjunction_i,
    first_conj,
    regexp_based_tag(r'^(([ivxlcdm]+)|([IVXLCDM]+))$', TAGS.ROM), # OK, this is not neccesarly roman number :)
    regexp_based_tag(r'^([0-9]{0,2}[\.\/]((0?[1-9])|(1[0-2]))[\.\/][1-9][0-9]{1,3})$', TAGS.DATE),
    month,
    abbreviation,
    regexp_based_tag(r'^(\w+)$', TAGS.WORD),
    regexp_based_tag(interp_regex, TAGS.INTERP),
    #regexp_based_tag(r'^(\w{1,3}\.)$', 'ABBR'),
    # Copy pasted regexp for url from: http://stackoverflow.com/questions/833469/regular-expression-for-url
    word_with_dot,
    regexp_based_tag(r'^(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+))*$', TAGS.WWW),
    comma_separated_tokens,
    hyphen_separated_tokens,
    regexp_based_tag(r'^[^@]+@[^@]+\.[^@]+', TAGS.EMAIL),
    unknown_token, # TODO: replace with always_word
]


def assign_tags(tokens):
  return itertools.chain.from_iterable(assign_tag(tokens, i) for i, token in enumerate(tokens))

def assign_tag(tokens, i):
  for fn in SIMPLE_TAG_FILTERS:
    tag = fn(tokens, i)
    if tag is not None:
      return tag
