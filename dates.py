#! /usr/bin/python

# -*- coding: utf-8 -*-

import re

from tags import TAGS

months = {
    TAGS.M_I : 1, TAGS.M_II : 2, TAGS.M_III : 3, TAGS.M_IV : 4,
    TAGS.M_V : 5, TAGS.M_VI : 6, TAGS.M_VII : 7, TAGS.M_VIII : 8,
    TAGS.M_IX : 9, TAGS.M_X : 10, TAGS.M_XI : 11, TAGS.M_XII : 12,
}

rom_months = {
    'i' : 1, 'I' : 1, 'ii' : 2, 'II' : 2, 'iii' : 3, 'III' : 3,
    'iv' : 4, 'IV' : 4, 'v' : 5, 'V' : 5, 'vi' : 6, 'VI' : 6,
    'vii' : 7, 'VII' : 7, 'viii' : 8, 'VIII' : 8, 'ix' : 9, 'IX' : 9,
    'x' : 10, 'X' : 10, 'xi' : 11, 'XI' : 11, 'xii' : 12, 'XII' : 12,
}

def parse_dates(tokens):
    tokens2 = []
    i = 0
    tks = list(tokens)
    while i < len(tks):
        word, tag = tks[i]
        if tag == TAGS.DATE:
            tag = TAGS.WORD
            m = re.match(r'(\d+).(\d+).(\d+)', word)
            if not m:
                m = re.match(r'(\d+)/(\d+)/(\d+)', word)
            if m:
                day, month, year = (int(x) for x in m.group(1, 2, 3))
                if day in xrange(1, 32) and month in xrange(1, 13):
                    tag = '%04d.%02d.%02d' % (year, month, day)
            i += 1
        elif i < len(tks) - 2:
            date = False
            day = None
            (word2, tag2), (word3, tag3) = tks[(i + 1):(i + 3)]
            if tag == TAGS.ARA and tag2 in months and tag3 == TAGS.ARA:
                day, month, year = int(word), months[tag2], int(word3)
            if tag == TAGS.ARA and tag2 == TAGS.ROM and word2 in rom_months and tag3 == TAGS.ARA:
                day, month, year = int(word), rom_months[word2], int(word3)
            if day:
                if day in xrange(1, 32) and month in xrange(1, 13):
                    tag = '%04d.%02d.%02d' % (year, month, day)
                    date = True
                    word = ' '.join((word, word2, word3))
                    i += 3
            # append r(.) to the date if present
            if date and i < len(tks):
                word4, tag4 = tks[i]
                if tag4 == TAGS.ABBR and word4 == 'r':
                    word += ' r'
                    i += 1
                    if i < len(tks) and tks[i][0] == '.':
                        word += '.' 
                        i += 1
            else:
                i += 1
        else:
            i += 1
        tokens2.append((word, tag))
    # Finally, replace unused month tags with word tag
    return [(word, TAGS.WORD if tag in months else tag) for (word, tag) in tokens2]
