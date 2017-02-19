#!/usr/bin/python
import re
import nltk
import sys
import getopt
import math
import string
from collections import defaultdict


class PostingModel:
    posting_list = defaultdict(lambda: defaultdict(list))
    vocabularies = {}

    def __init__(self, ):
        pass
    
def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file "


directory_of_documents = dictionary_file = postings_file = None;



try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')

except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        directory_of_documents = a
    elif o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    else:
        assert False, "unhandled option"
if directory_of_documents == None or dictionary_file == None or postings_file == None:
    usage()
    sys.exit(2)

