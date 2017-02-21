#!/usr/bin/python
import re
import nltk
import sys
import getopt
import math
import string
import os
import numpy as np
from collections import defaultdict
from nltk import sent_tokenize
from nltk.tokenize import RegexpTokenizer
import pprint
TEST = True
DEBUG = True
directory_of_documents = dictionary_file = postings_file = None

class PostingModel:
    posting_list = defaultdict(list)
    vocabularies = defaultdict(list)
    tokenizer = RegexpTokenizer(r'\w+')

    def __init__(self, directory_of_documents, dictionary_file, postings_file):
        self.directory_of_documents = directory_of_documents
        self.dictionary_file = dictionary_file
        self.postings_file = postings_file


    def buildIndex(self):
        filenames = os.listdir(self.directory_of_documents)
        if TEST:
            filenames = filenames[:50]
        for filename in filenames:
            self._buildIndex(filename)
        if DEBUG:
            pprint.pprint(self.posting_list)
            pprint.pprint(self.vocabularies)

    def _buildIndex(self, filename):
        tf = open(self.directory_of_documents + filename)
        tokens = []
        for lines in tf:
            tokens = tokens + self.tokenizer.tokenize(lines.lower())
        tokens = set(tokens)

        for token in tokens:
            self.posting_list[token].append(filename)
            if token not in self.vocabularies:
                self.vocabularies[token] = [0, ""];
            self.vocabularies[token][0] += 1

        if DEBUG:
            print(filename)
            pprint.pprint(tokens)

    def saveFile(self):
        df = open(self.dictionary_file, "w+")
        pf = open(self.postings_file, "w+")
        for word in self.vocabularies:
            self.vocabularies[word][1] = pf.tell()
            pf.write(" ".join(list(map(str, self.posting_list[word])))+"\n")
            df.write("%s,%s,%s\n"%(word, str(self.vocabularies[word][0]),str(self.vocabularies[word][1])))
            if DEBUG:
                print("Dict:"+"%s,%s,%s\n"%(word, str(self.vocabularies[word][0]),str(self.vocabularies[word][1])))
                print("Posting Docs:"+" ".join(list(map(str, self.posting_list[word])))+"\n")
        pf.close()
        df.close()

    def loadDictionary(self):
        df = open(self.dictionary_file, "r")
        pf = open(self.postings_file, "r")
        wordDictionay = {}
        for line in df:
            word, freq, pointer = line.strip().split(",")
            wordDictionay[word] = [int(freq), int(pointer)]
        df.close()
        return wordDictionay

    def getPostingList(self, word, wordDictionay):
        pf = open(self.postings_file, "r")
        pf.seek(wordDictionay[word][1],0)
        pl = pf.readline().strip()
        print(word, wordDictionay[word][0], wordDictionay[word][1], pl)
        pl = list(map(int, pl.split(" ")))
        return pl



def usage():
    print directory_of_documents, dictionary_file, postings_file
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file "




try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    print err.msg
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

pm = PostingModel(directory_of_documents, dictionary_file, postings_file )
pm.buildIndex()
pm.saveFile()

wd = pm.loadDictionary()
pprint.pprint(wd)
pprint.pprint(pm.getPostingList("years", wd))