# -*- coding: utf-8 -*-
"""
mecab.py: This file invokes the Mecab morphological analyser on the
cleaned input files and parses its output, storing word information
like pos and root and associating them with the sentences.
Then it inserts these into the given database.
"""

import sys
import re
import MeCab

import config
from logger import logger

class PyMeCab():
  def __init__(self, sentences):
    self.sentences = sentences
    self.tagger = MeCab.Tagger('')
    self.fields = config.mecab_fields
    # mecab has somtimes an error on the first parse, so test this before
    self.tagger.parseToNode(u'日本語'.encode('utf-8'))

  def parse(self, line, db):
    node = self.tagger.parseToNode(line.encode('utf-8'))
    # accumulate words until end of stream or sentence
    while node:
      if node.stat == MeCab.MECAB_BOS_NODE:
        sentence = u''
        data = []
      elif node.stat == MeCab.MECAB_NOR_NODE or node.stat == MeCab.MECAB_UNK_NODE:
        try:
          word = node.surface.decode('utf-8')
          fields = node.feature.decode('utf-8').split(',')
          # get part-of-speech features 
          pos = fields[0:self.fields]
          if fields[6] != u'*': # if root form is available, use it
            root = fields[6] 
          else:
            root = word
          sentence = sentence + word
          data.append([root] + pos)
          if pos[0] == u'記号' and pos[1] == u'句点' \
            or pos[0] == u'記号' and word == u'！' \
            or pos[0] == u'記号' and word == u'？':
            self.insert(data, sentence, db)
            sentence = u''
            data = []
        except UnicodeDecodeError as e:
          logger.err('could not decode %s' % node.surface)
      elif node.stat == MeCab.MECAB_EOS_NODE:
        self.insert(data, sentence, db)
      node = node.next

  def insert(self, data, sentence, db):
    if self.sentences and sentence != '':
      sid = db.insert_sentence(sentence)
    for fieldvalues in data:
      wid = db.insert_word(fieldvalues)
      if self.sentences:
        assert wid > 0 and sid > 0
        db.insert_link(wid, sid)

