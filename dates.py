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

clean_up = {m : TAGS.WORD for m in months}
clean_up[TAGS.INT] = TAGS.ARA

def parse_dates(tokens):
    tokens2 = []
    i = 0
    tks = list(tokens)
    while i < len(tks):
        word, tag = tks[i]
        date = False
        if tag == TAGS.DATE:
            tag = TAGS.WORD
            m = re.match(r'(\d+).(\d+).(\d+)', word)
            if not m:
                m = re.match(r'(\d+)/(\d+)/(\d+)', word)
            if m:
                day, month, year = (int(x) for x in m.group(1, 2, 3))
                if day in xrange(1, 32) and month in xrange(1, 13):
                    tag = '%04d.%02d.%02d' % (year, month, day)
                    date = True
            i += 1
        elif i < len(tks) - 2:
            day = None
            (word2, tag2), (word3, tag3) = tks[(i + 1):(i + 3)]
            # 11 marca 2014
            if tag == TAGS.INT and tag2 in months and tag3 == TAGS.INT:
                day, month, year = int(word), months[tag2], int(word3)
            # 11 III 2014
            if tag == TAGS.INT and tag2 == TAGS.ROM and word2 in rom_months and tag3 == TAGS.INT:
                day, month, year = int(word), rom_months[word2], int(word3)
            # 2014 11 marca - strange, but found in NKJP
            if tag == TAGS.INT and tag2 == TAGS.INT and tag3 in months:
                day, month, year = int(word2), months[tag3], int(word)
            if day:
                if day in xrange(1, 32) and month in xrange(1, 13):
                    tag = '%04d.%02d.%02d' % (year, month, day)
                    date = True
                    word = ' '.join((word, word2, word3))
                    i += 3
            # 2014, 11 marca - strange, but found in NKJP
            if not date and i < len(tks) - 3:
                (word4, tag4) = word4, tag4 = tks[i + 3]
                if tag == TAGS.INT and word2 == u',' and tag3 == TAGS.INT and tag4 in months:
                    day, month, year = int(word3), months[tag4], int(word)
                    if day in xrange(1, 32) and month in xrange(1, 13):
                        tag = '%04d.%02d.%02d' % (year, month, day)
                        date = True
                        word = '%s, %s %s' % (word, word3, word4)
                        i += 4
            if not date:
                i += 1
        else:
            i += 1
        # append roku / r(.) to the date if present
        if date and i < len(tks):
            w, t = tks[i]
            if w == u'r':
                word += u' r'
                i += 1
                if i < len(tks) and tks[i][0] == u'.':
                    word += '.' 
                    i += 1
            if w == u'roku':
                word += u' roku'
                i += 1
        tokens2.append((word, tag))
    # Replace unused month tags with word tag
    # Replace unused int tags with ara tag
    return [(word, clean_up[tag] if tag in clean_up else tag) for (word, tag) in tokens2]
