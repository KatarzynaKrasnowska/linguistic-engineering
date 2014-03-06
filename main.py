#! /usr/bin/python

# -*- coding: utf-8 -*-

import codecs
import re
import sys

from dates import parse_dates
from ext_tokenizer_xml_parsing import make_parser, TreeHandler
from token import assign_tags

interpunction = '():;-'

def tokenize_sentence(sentence):
    words = []
    for w in sentence.split(' '):
        ws = [token.strip() for token in re.split('^([\:\;\-\?\!\(\)])', w, re.UNICODE) if token.strip()]
        words += ws[:-1]
        w = ws[-1]
        words += [token.strip() for token in re.split('([\:\;\-\?\!\(\)])$', w, re.UNICODE) if token.strip()]
    return parse_dates(assign_tags(words))

def main():
    if len(sys.argv) < 3:
        print 'Usage: main.py <input_xml> <output_xml>'
        return
    input_xml = sys.argv[1]
    output_xml = sys.argv[2]
    with codecs.open(output_xml, encoding='utf_8', mode='w') as output:
        parser = make_parser()
        parser.setContentHandler(TreeHandler(output))
        parser.parse(input_xml)
        tree = parser.getContentHandler()
        sentence = tree.getNextSentence()
        while sentence is not None:
            words = sentence.split(' ')
            tokens = tokenize_sentence(sentence)
            tree.setTokenization(tokens)
            sentence = tree.getNextSentence()
        tree.printTokenization()

if __name__ == '__main__':
    main()
