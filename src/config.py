"""
config.py: This file stores default configuration options.
"""

import sys
import os.path

# string to use for displaying all entries
ALL = u'*'
  
formatter = 'aozora'
encoding  = 'utf-8'
output    = None
dbfile    = 'data/freqs.db'
tablename = 'main'
gaijifile ='data/jisx0213-2004-8bit-std.txt'
mecab_fields = 5 # mecab pos fields, should not change
list_number = 100 # number of items to display in list

def get_basedir():
  return os.path.normpath(os.path.join(
      os.path.split(sys.argv[0])[0], os.pardir))
