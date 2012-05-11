# -*- coding: utf-8 -*-
"""
mecab.py: This file invokes the Mecab morphological analyser on the
cleaned input files and parses its output for further processing.
"""

import sys
import re
import MeCab

from logger import logger

class MecabData():
  def __init__(self, word, pos):
    self.word = word
    self.pos = pos

  def __repr__(self):
    return self.word + u' (' + u','.join(self.pos) + u')'

  def __hash__(self):
    return hash(self.__repr__())

  def __eq__(self, other):
    if self.word != other.word:
      return False
    for i in range(len(self.pos)):
      if self.pos[i] != other.pos[i]:
        return False
    return True

  def __cmp__(self, other):
    if self.word < other.word:
      return -1
    elif self.word > other.word:
      return 1
    else:
      for i in range(len(self.pos)):
        if self.pos[i] < other.pos[i]:
          return -1
        elif self.pos[i] > other.pos[i]:
          return 1
    return 0

class PyMeCab():
  def __init__(self):
    self.tagger = MeCab.Tagger('')

  def parse(self, line):
    node = self.tagger.parseToNode(line.encode('utf-8'))
    data = []
    while node:
      if node.stat == 0 or node.stat == 1: # MECAB_NOR_NODE or MECAB_UNK_NODE
        try:
          word = node.surface.decode('utf-8')
          fields = node.feature.decode('utf-8').split(',')
          # get part-of-speech features 
          #print('node %s with type %s and len %s' % (word, type(word), len(word)))
          pos = fields[0:6]
          if fields[6] != '*': # take root instead of conjugation
            word = fields[6] 
          data.append(MecabData(word, pos))
        except UnicodeDecodeError as e:
          logger.err('could not decode %s' % node.surface)
      # else MECAB_BOS_NODE or MECAB_EOS_NOD, ignore
      node = node.next
    return data
