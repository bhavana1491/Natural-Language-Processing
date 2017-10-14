#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
import string
punctuation = string.punctuation
punctuation = punctuation+'``'

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)

vowels = "aeiou"

class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()

    def apostrophe_tokenize(self,line):
        line = line.lower()
        lst = [word.strip(string.punctuation) for word in line.split(" ")]
        filtered = filter(None, lst)
        return filtered

    def guess_syllables(self, word):
        w = word.lower()
        sylCount = 0
        subSyl = 0
        if len(w) <= 3:
            sylCount = 1
            return sylCount
        numVow = len(re.findall(r'[aeiou]', w))
        if w[-1:] == "y" and w[-2] not in vowels:
            sylCount += 1
        for i, j in enumerate(w):
            if j == "y":
                if (i != 0) and (i != len(w) - 1):
                    if w[i - 1] not in vowels and w[i + 1] not in vowels:
                        sylCount += 1
        diphthong = len(re.findall(r'[aeiou][aeiou]',w))
        triphthong = len(re.findall(r'[aeiou][aeiou][aeiou]',w))
        subSyl += diphthong + triphthong
        if re.search("[^aeioul]e$",w):
            subSyl+=1
        if re.search("[aeiou]les?",w):
            subSyl += 1

        return numVow - subSyl + sylCount

    def removeFirstConsonant(self, word):
        for i in range(0, len(word)):
            if word[i][0].lower() in vowels:
                cWord = word[i:]
                if len(cWord) == 0:
                    return word
                else:
                    return cWord

    def checkSylConstraint(self,syCount):
        aMin = min(syCount[0], syCount[1], syCount[4])
        aMax = max(syCount[0], syCount[1], syCount[4])
        bMin = min(syCount[2], syCount[3])
        bMax = max(syCount[2], syCount[3])
        for i in syCount:
            if i < 4:
                return False
            if abs(aMax - aMin) > 2 or abs(bMax - bMin) > 2:
                return False
            else:
                if syCount[2] < aMin and syCount[3] < aMin:
                    return True
                else:
                    return False



    def isSubset(self,l1, l2):
        m = [len(x) for x in l1]
        n = [len(x) for x in l2]
        spIdx = min(min(m), min(n))
        listA = []
        listB = []
        for x in l1:
            listA.append(x[-spIdx:])
        for x in l2:
            listB.append(x[-spIdx:])
        if len(listA) > len(listB):
            maxL = listA
            minL = listB
        else:
            if len(listB) > len(listA):
                maxL = listB
                minL = listA
            else:
                maxL = listA
                minL = listB
        return all(x in maxL for x in minL)


    def num_syllables(self, word):

        """
                Returns the number of syllables in a word.  If there's more than one
                pronunciation, take the shorter one.  If there is no entry in the
                dictionary, return 1.
                """
        word = word.lower()

        if word in self._pronunciations:
            w = min(self._pronunciations[word], key=len)
            nsyl = []

            for ch in w:
                if ch[-1].isdigit():
                    nsyl.append(ch)
            return len(nsyl)
        else:
            return 1

    def rhymes(self, a, b):

        """
                Returns True if two words (represented as lower-case strings) rhyme,
                False otherwise.
                """
        aSounds = self._pronunciations[a]
        bSounds = self._pronunciations[b]
        print aSounds, bSounds
        for id, i in enumerate(aSounds):
            aSounds[id] = self.removeFirstConsonant(i)
        for id, j in enumerate(bSounds):
            bSounds[id] = self.removeFirstConsonant(j)

        res = self.isSubset(aSounds, bSounds)
        if res is True:
            return True
        else:
            return False




    def is_limerick(self, text):
        """
                    Takes text where lines are separated by newline characters.  Returns
                    True if the text is a limerick, False otherwise.

                    A limerick is defined as a poem with the form AABBA, where the A lines
                    rhyme with each other, the B lines rhyme with each other, and the A lines do not
                    rhyme with the B lines.


                    Additionally, the following syllable constraints should be observed:
                      * No two A lines should differ in their number of syllables by more than two.
                      * The B lines should differ in their number of syllables by no more than two.
                      * Each of the B lines should have fewer syllables than each of the A lines.
                      * No line should have fewer than 4 syllables

                    (English professors may disagree with this definition, but that's what
                    we're using here.) """
        text = text.strip('""')
        text = "".join([s for s in text.strip().splitlines(True) if s.strip()])
        print "Input Text", text
        if "\n" in text:
            lines = text.splitlines()
        lines = text.splitlines()
        nLines = len(lines)
        print "Number of Lines" , nLines
        if not (nLines < 5 or nLines > 5):
            print "Inside isLimerick"
            endWords = []
            syCount = []
            for id in range(0, nLines):
                sylCount = []
                line = lines[id].lower()
                words = word_tokenize(line)
                newWords = [i for i in words if i not in punctuation]
                newWords = [x for x in newWords if not re.match("'", x)]
                endWords.append(newWords[-1])
                for w in newWords:
                    sylCount.append(self.num_syllables(w))
                print "SylCount", sylCount
                syCount.append(sum(c for c in sylCount))
            print syCount
            print endWords
            aRhyme = self.rhymes(endWords[0], endWords[1])
            bRhyme = self.rhymes(endWords[2], endWords[3])
            if aRhyme is True:
                aLinesRhyme = self.rhymes(endWords[0], endWords[4])
                if aLinesRhyme is True and bRhyme is True:
                    sylConstraint = self.checkSylConstraint(syCount)
                    if sylConstraint is True:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False


        # TODO: provide an implementation!
        else:
            return False


# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))
if __name__ == '__main__':
  main()
