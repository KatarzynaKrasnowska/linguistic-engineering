#! /usr/bin/python

# -*- coding: utf-8 -*-

import codecs
import re
import sys

colors = {
    'word' : 'white',
    'ara' : 'DarkSeaGreen',
    'rom' : 'LightSteelBlue',
    'abbrev' : 'Khaki',
    'punct' : 'LightSalmon',
}

def tag_color(tag):
    if tag in colors:
        return colors[tag]
    return 'LightCoral'

def main():
    input_xml = sys.argv[1]
    output_html = sys.argv[1].replace('.xml', '.html')
    with codecs.open(input_xml, encoding='utf_8', mode='r') as xml:
        with codecs.open(output_html, encoding='utf_8', mode='w') as html:
            html.write('<!DOCTYPE html>\n<head><meta charset="UTF-8"></head>\n<body>\n<table>')
            for l in xml.readlines():
                match = re.match(r'.*<token>(.+)</token>.*', l, re.UNICODE)
                if match:
                    html.write('<tr><td>%s</td>' % match.group(1))
                match = re.match(r'.*<tag>(.+)</tag>.*', l, re.UNICODE)
                if match:
                    tag = match.group(1)
                    color = tag_color(tag)
                    html.write('<td style="background-color:%s;"><i>%s</i></td></tr>\n' % (color, tag))
                match = re.match(r'.*</s>.*', l, re.UNICODE)
                if match:
                    html.write('<tr><td>&nbsp</td><td>&nbsp</td></tr>\n')
            html.write('</table>\n</body>\n')

if __name__ == '__main__':
    main()
