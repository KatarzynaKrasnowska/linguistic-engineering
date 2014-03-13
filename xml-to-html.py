#! /usr/bin/python

# -*- coding: utf-8 -*-

import codecs
import re
import sys

def main():
    input_xml = sys.argv[1]
    output_html = sys.argv[1].replace('.xml', '.html')
    with codecs.open(input_xml, encoding='utf_8', mode='r') as xml:
        with codecs.open(output_html, encoding='utf_8', mode='w') as html:
            html.write('<!DOCTYPE html>\n<head><meta charset="UTF-8"></head>\n\n<body>\n<table>')
            for l in xml.readlines():
                match = re.match(r'.*<token>(.+)</token>.*', l, re.UNICODE)
                if match:
                    html.write('<tr><td>%s</td>' % match.group(1))
                match = re.match(r'.*<tag>(.+)</tag>.*', l, re.UNICODE)
                if match:
                    html.write('<td><i>%s</i></td></tr>\n' % match.group(1))
            html.write('</table>\n</body>\n')

if __name__ == '__main__':
    main()
