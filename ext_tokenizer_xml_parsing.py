#! /usr/bin/python

# -*- coding: utf-8 -*-

import sys, os
from xml.sax import saxutils, handler, make_parser

def spaces(count = 0):
    result = ''
    i = 0
    while i < count:
        result += ' '
        i += 1
    return result 

class Sentence:

    def __init__(self, text=None):
        self._text = text
        self._tokens = [] # list of pairs (token, type)
    
    def __str__(self):
        return '(%s)' % self._text

    def getText(self):
        return self._text

    def setTokens(self, tokens):
        self._tokens = tokens

    def printTokenization(self,sent_id, out = sys.stdout, ident = 0):
        count = 0
        for (token, tag) in self._tokens:
            count += 1
            token_id = sent_id.replace('s', '%d-seg' % count)
            out.write(spaces(ident) + '<seg xml:id="%s">\n' % token_id)
            out.write(spaces(ident + 1) + '<token>' + token + '</token>\n')
            out.write(spaces(ident + 1) + '<tag>' + tag + '</tag>\n')
            out.write(spaces(ident) + '</seg>\n')

class TreeNode:

    def __init__(self):
        self._id = ' '
        self._type = ' '
        self._children = []
        self._content = None
        self._next = None
        self._parent = None

    def __str__(self):
        result = '%s(' % self._id
        for child in self._children:
            result += str(child)
        result += ')'
        return result

# printing output xml from tree

    def printTokenization(self, out = sys.stdout, ident = 0):
        if self._type == 't':
            out.write(spaces(ident) + '<?xml version="1.0" encoding="UTF-8"?>\n')
            out.write(spaces(ident) + '<text>\n')
            for child in self._children:
                child.printTokenization(out, ident + 1)
            out.write(spaces(ident) + '</text>\n')
        elif self._type == 'p':
            out.write(spaces(ident) + '<p xml:id="%s">\n' % self._id)
            for child in self._children:
                child.printTokenization(out, ident + 1)
            out.write(spaces(ident) + '</p>\n')
        elif self._type == 's':
            out.write(spaces(ident) + '<s xml:id="%s">\n' % self._id)
            self._content.printTokenization(self._id, out, ident + 1)
            out.write(spaces(ident) + '</s>\n')
        else:
            print 'WARNING: Unknown type of tree node (%s); node ignored\n' % self._type     
    
class TreeHandler(handler.ContentHandler):

    def __init__(self, out = sys.stdout):
        handler.ContentHandler.__init__(self)
        self._out = out
        self._root = None
        # for leaf walk
        self._walk = None
        self._walk_start = True
        # for generating
        self._current = None
        self._parent = None
        self._sentence = False

# generating tree from xml
    
    def startElement(self, name, attrs):
        self._current = TreeNode()
        self._sentence = False
        if (name == 'text'):
            self._root = self._current
            self._current._type = 't'
        elif (name == 'p'):
            cid = attrs['xml:id']
            self._current._id = cid
            self._current._type = 'p'
            self._root._children.append(self._current)
            self._parent = self._current
        elif (name == 's'):
            cid = attrs['xml:id']
            self._current._type = 's'
            self._current._id = cid
            self._parent._children.append(self._current)
            self._sentence = True
        else:
            print 'WARNING: unknown element in xml structure (%s); element ignored\n' % name

#    def endElement(self, name):
#        pass        

    def characters(self, content):
        if (self._sentence and content.strip()):
            if self._current._content is None:
              self._current._content = Sentence(content)
            else:
              self._current._content._text += ' ' + content

# initializing leaf walk

    def endDocument(self):
        last = None
        last = self._initWalk(last)

    def _initWalk(self, last, subtree_root = None):
        if subtree_root is None:
            subtree_root = self._root
        if len(subtree_root._children) == 0:
            if last is None:
                self._walk = subtree_root
            else:
                last._next = subtree_root
            last = subtree_root
        else:
            for child in subtree_root._children:
                last = self._initWalk(last, child)
        return last

# leaf walk
        
    def getNextSentence(self):
        if not self._walk_start:
            self._walk = self._walk._next
        else:
            self._walk_start = False
        if self._walk is None:
            return None
        return self._walk._content.getText()

    def setTokenization(self, tokens):
        self._walk._content.setTokens(tokens)

# output

    def printTokenization(self):
        self._root.printTokenization(self._out)

    def __str__(self):
        return 'tree(%s)' % str(self._root)
