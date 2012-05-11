#!/usr/bin/env python2

"""
This is the Japanese Novel Analyser.
It reads in novels from files in aozora formatting, strips this formatting,
invokes the mecab morphological analysis and counts word frequencies.

Usage: analyser.py [OPTION]... FILE..
Read and analyse each FILE.

Options:
  -h, --help          Display this help
  -e, --encoding=ENC  Set the encoding for the files to ENC
  -f, --format=FORMAT Set the format of the files;
                      FORMAT is  'plain', 'aozora' or 'html`
  -o, --output=FILE   Write cleaned up up input file to FILE
"""

import sys
import getopt
import codecs
import os.path

import formats
import mecab
import freq
from logger import logger

def main():
  # get path of main program directory
  basedir =  os.path.normpath(os.path.join(
      os.path.split(sys.argv[0])[0], os.pardir))
  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'hf:e:o:', ['help','format=','encoding=', 'output='])
  except getopt.error as opterr:
    logger.err(opterr)
    logger.err('for help use --help')
    sys.exit(2)
  # process options
  formatter = 'aozora'
  encoding = 'utf-8'
  output = None
  for o, a in opts:
    if o in ('-h', '--help'):
      logger.out(__doc__)
      sys.exit(0)
    if o in ('-f', '--format'):
      formatter = a
      if formatter not in ('plain', 'aozora', 'html'):
        logger.err('format not supported: %s' % formatter)
        sys.exit(2)
    if o in ('-e', '--encoding'):
      encoding = a
      try:
        codecs.lookup(encoding)
      except LookupError:
        logger.err('encoding not found: %s' % encoding)
        sys.exit(2)
    if o in ('-o', '--output'):
      try:
        output = open(a, 'w')
      except IOError as e:
        logger.err('error opening %s: %s' % (a, e))
  # create formatter and parser
  if(formatter == 'aozora'):
    formatter = formats.AozoraFormat(basedir)
  elif(formatter == 'html'):
    formatter = formats.HtmlFormat()
  else:
    formatter = formats.Format()
  parser = mecab.PyMeCab()
  try:
    # process files
    logger.out('analyzing text files')
    analyze(args, formatter, parser, encoding, output)
    logger.out('done analyzing')
  finally:
    if output:
      output.close()

def analyze(files, formatter, parser, encoding, output):
  freqcounter = freq.FrequencyCounter()
  # process all files line by line
  for filename in files:
    logger.out('reading %s' % filename)
    formatter.new_file()
    try:
      fp = codecs.open(filename, 'r', encoding)
    except IOError as e:
      logger.err('error opening %s: %s' % (filename, e))
    else:
      with fp:
        for line in fp:
          trimmed_line = formatter.trim(line)
          mecab_data = parser.parse(trimmed_line)
          if output:
            output.write(trimmed_line.encode('utf-8'))
          for word_data in mecab_data:
            freqcounter.add_word(word_data)
          #TODO: continue counting word frequencies 

if __name__ == '__main__':
  main()
