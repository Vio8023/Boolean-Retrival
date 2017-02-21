import re
import nltk
import sys
import getopt
from math import log
from operator import add
import io
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import RegexpTokenizer

class Search:
    allDocid = None
    dicitonary_file = posting_file = query_file = None
    pf = None
    wordDictionay = {}
    tokenizer = RegexpTokenizer(r'\w+')

    def __init__(self, d, p, q):
        self.dicitonary_file = d
        self.posting_file = p
        self.query_file = q
        self.loadDictionary()
        self.processBoolQueries()
        self.pf.close()

    def processBoolQueries(self):
        priority = {'AND': 1, 'OR': 1, 'NOT': 2}
        with io.open(self.query_file) as qf:
            for query in qf:
                words = self.tokenizer.tokenize(query)
                length = len(words)

                stack = []
                op = []
                for i in range(length):
                    if words[i] == 'AND' or words[i] == 'OR' or words[i] == 'NOT':
                        while not op and priority[op[len(op) - 1]] >= priority[words[i]]:
                            stack = self.processOp(op.pop(), stack)
                        op.append(words[i])

                    if words[i] == '(':
                        op.append('(')

                    if words[i] == ')':
                        while op[len(op) - 1] != '(':
                            stack = self.processOp(op.pop(), stack)
                        op.pop()

                    else:
                        # to add: stemming & word processing
                        stack.append(self.getPostingList(words[i].lower()))

                while not op:
                    stack = self.processOp(op.pop(), stack)

                list_to_print = ' '.join(stack[0])
                print list_to_print
        return

    def processOp(self, op, stack):
        if op == 'AND':
            list1 = stack.pop()
            list2 = stack.pop()
            stack.append(self.intersection(list1, list2))
        if op == 'OR':
            list1 = stack.pop()
            list2 = stack.pop()
            stack.append(self.intersection(list1, list2))
        if op == 'NOT':
            list = stack.pop()
            stack.append(self.complement(list))
        return stack

    def intersection(self, list1, list2):
        return list(set(list1) & set(list2))

    def merge(self, list1, list2):
        return list(set(list1 + list2))

    def complement(self, list):
        return list(set(self.allDocid) - set(list))

    def loadDictionary(self):
        df = open(self.dictionary_file, "r")
        self.pf = open(self.postings_file, "r")
        self.allDocid = list(df.readline().strip().split(' '))
        for line in df:
            word, freq, pointer = line.strip().split(",")
            self.wordDictionay[word] = [int(freq), int(pointer)]
        df.close()
        return

    def getPostingList(self, word):
        # pf = open(self.postings_file, "r")
        self.pf.seek(self.wordDictionay[word][1],0)
        pl = self.pf.readline().strip()
        print(word, self.wordDictionay[word][0], self.wordDictionay[word][1], pl)
        pl = list(map(int, pl.split(" ")))
        return pl

# $ python search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results
d = p = q = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        d = a
    elif o == '-p':
        p = a
    elif o == '-q':
        q = a
    else:
        assert False, "unhandled option"
if d == None or p == None or q == None:
    # usage()
    sys.exit(2)

Search(d, p, q)

# LM = build_LM(input_file_b)
# test_LM(input_file_t, output_file, LM)