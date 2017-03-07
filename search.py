import re
import nltk
import sys
import getopt
from math import log
from operator import add
import io
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk import stem
import pprint
DEBUG = False

class Search:
    allDocid = None
    dictionary_file = posting_file = query_file = output_file = None
    pf = of = None
    wordDictionary = {}
    tokenizer = RegexpTokenizer(r'(\w+|\(|\))+')

    def __init__(self, d, p, q, o):
        self.dictionary_file = d
        self.posting_file = p
        self.query_file = q
        self.output_file = o
        self.loadDictionary()
        self.processBoolQueries()
        self.pf.close()
        self.of.close()

    def processBoolQueries(self):
        priority = {'AND': 1, 'OR': 1, 'NOT': 2, '(': 0}
        with io.open(self.query_file) as qf:
            for query in qf:
                query = query.replace('(', ' ( ').replace(')', ' ) ')
                words = self.tokenizer.tokenize(query.strip())
                length = len(words)
                if DEBUG:
                    print words
                stack = []
                op = []
                for i in range(0, length):
                    if words[i] == 'AND' or words[i] == 'OR' or words[i] == 'NOT':
                        if DEBUG:
                            print op
                        while (len(op) > 0) and priority[op[len(op) - 1]] >= priority[words[i]]:
                            stack = self.processOp(op.pop(), stack)
                        op.append(words[i])

                    elif words[i] == '(':
                        op.append('(')

                    elif words[i] == ')':
                        while len(op) > 0 and op[len(op) - 1] != '(':
                            stack = self.processOp(op.pop(), stack)
                        op.pop()

                    else:
                        # stemming & word processing
                        stemmer = stem.PorterStemmer()
                        stack.append(self.getPostingList(stemmer.stem(words[i].lower())))


                while len(op) > 0:
                    stack = self.processOp(op.pop(), stack)

                res = stack[0]
                res.sort(key = int)
                list_to_print = ' '.join(list(map(str, res))) + "\n"
                self.of.write(list_to_print)
                if DEBUG:
                    print list_to_print
        return

    def processOp(self, op, stack):
        if op == 'AND':
            list1 = stack.pop()
            list2 = stack.pop()
            stack.append(self.intersection(sorted(list1), sorted(list2)))
        elif op == 'OR':
            list1 = stack.pop()
            list2 = stack.pop()
            stack.append(self.merge(list1, list2))
        elif op == 'NOT':
            list1 = stack.pop()
            stack.append(self.complement(list1))
        if DEBUG:
            print stack
        return stack


    def intersection(self, list1, list2):
         """Skip pointer used to find intersection of two list
         """
         l1pnt = 0
         l2pnt = 0
         ans = []
         len1 = len(list1)
         len2 = len(list2)

         """Calculate skip pointer length
         """
         SKIP_LENGTH1 = int(len1**0.5)
         SKIP_LENGTH2 = int(len2**0.5)

         """Loop through two list to check element
         """
         while l1pnt < len1 and l2pnt < len2:
             if list1[l1pnt] == list2[l2pnt]:
                 ans.append(list1[l1pnt])
                 l1pnt+=1
                 l2pnt+=1
                 continue
             if l1pnt + SKIP_LENGTH1 < len1 and list1[l1pnt + SKIP_LENGTH1] < list2[l2pnt]:
                 while l1pnt + SKIP_LENGTH1 < len1 and list1[l1pnt + SKIP_LENGTH1] < list2[l2pnt]:
                    l1pnt += SKIP_LENGTH1
                 continue

             if l2pnt + SKIP_LENGTH2 < len2 and list2[l2pnt + SKIP_LENGTH2] < list1[l1pnt]:
                 while l2pnt + SKIP_LENGTH2 < len2 and list2[l2pnt + SKIP_LENGTH2] < list1[l1pnt]:
                     l2pnt += SKIP_LENGTH1
                 continue
             if list1[l1pnt] < list2[l2pnt]:
                 l1pnt += 1
             else:
                 l2pnt += 1

         if DEBUG:
            print(len(set(ans)), len(set(list1) & set(list2)))
         #assert (set(ans) == set(list1) & set(list2))
         return ans

        # return list(set(list1) & set(list2))

    def merge(self, list1, list2):
        return list(set(list1 + list2))

    def complement(self, list1):
        return list(set(self.allDocid) - set(list1))

    def loadDictionary(self):
        df = open(self.dictionary_file, "r")
        self.pf = open(self.posting_file, "r")
        self.of = open(self.output_file, "w+")
        self.allDocid = list(df.readline().strip().split(' '))
        for line in df:
            word, freq, pointer = line.strip().split(",")
            self.wordDictionary[word] = [int(freq), int(pointer)]
        df.close()
        return

    def getPostingList(self, word):
        # pf = open(self.postings_file, "r")
        if word in self.wordDictionary:
            self.pf.seek(self.wordDictionary[word][1],0)
            pl = self.pf.readline().strip()
            if DEBUG:
                print(word, self.wordDictionary[word][0], self.wordDictionary[word][1], pl)


            pl = list(map(int, pl.split(" ")))
        else:
            pl = []
        return pl

def usage():
    print d, p, q, o
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results "


# $ python search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results
d = p = q = o = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    print err.msg
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        d = a
    elif o == '-p':
        p = a
    elif o == '-q':
        q = a
    elif o == '-o':
        o = a
    else:
        assert False, "unhandled option"
if d == None or p == None or q == None or o == None:
    usage()
    sys.exit(2)

Search(d, p, q, o)

# LM = build_LM(input_file_b)
# test_LM(input_file_t, output_file, LM)