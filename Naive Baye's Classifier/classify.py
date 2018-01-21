#!/usr/bin/env python
from collections import defaultdict,Counter
#import pronouncing
from csv import DictReader, DictWriter
import gzip
import nltk
import codecs
import sys
import re
import string
from nltk.corpus import wordnet as wn
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import cmudict
kTOKENIZER = TreebankWordTokenizer()
pronunciations = cmudict.dict()

def morphy_stem(word):
    """
    Simple stemmer
    """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()

class FeatureExtractor:
    def __init__(self):
        """
        You may want to add code here
        """

        None

    def stress_word(self,pron):
        """
        get the stress pattern of a word's pronounciation
        this is copied from the NLTK book
        """

        return [char for phone in pron for char in phone if char.isdigit()]

    def stress_line(self,line):
        """get the stress pattern of a line"""
        stress_pattern = []
        line = line.lower()
        # split the line into words (strip away punctuation)
        words = [word.strip(string.punctuation) for word in line.split()]
        #words = line.split()
        # find stress pattern for each word
        # and add it to the stress pattern of the line
        for word in words:
            # find pronounciation of word
            # there might be more than one pronounciation,
            # get the first one for convenience
            if word in pronunciations:
                pron = pronunciations[word][0]
                stress_pattern += self.stress_word(pron)

        return stress_pattern

    def ngrams(self,words, n=2, padding=False):
        "Compute n-grams with optional padding"
        pad = [] if not padding else [None] * (n - 1)
        grams = pad + words + pad
        return (tuple(grams[i:i + n]) for i in range(0, len(grams) - (n - 1)))

    def num_syllables(self,word):

        word = word.lower()
        #word = word.replace("'d",'ed')
        if word in pronunciations:
            w = min(pronunciations[word], key=len)
            nsyl = []

            for ch in w:
                if ch[-1].isdigit():
                    nsyl.append(ch)
            return len(nsyl)
        else:
            return 1

    def sumSyllables(self, line):
        words = line.split()
        sylCount = []
        for w in words:
            sylCount.append(self.num_syllables(w))
        return sum(c for c in sylCount)

    def isIambic(self,text):

        return self.sumSyllables(text) == 10

    def features(self, text):
        d = defaultdict(int)
        text = text.replace(',','')
        #print self.stress_line("Then how, when nature calls thee to be gone,")
        #d['words'] = len(nltk.word_tokenize(text))
        words = text.split(" ")
        '''w = [word.strip(string.punctuation) for word in words]
        w = filter(None, w)'''
        #print w
        #d['words'] = len(w)
        #d['senLen'] = len(text)
        '''search = text.lower()
        vo = {v: search.count(v) for v in 'aeiou'}
        d['vowels'] = sum(vo.itervalues())'''
        '''v = re.findall(r'(?:\s|^)([\w\']+)\b', text)
        count = []
        for x in v:
            acount = 0
            count.append(re.findall(r"(?=\S*['-])([a-zA-Z'-]+)", x))
        #print count
        for c in count:
            if len(c) != 0:
                acount += 1
        d['ap'] = acount'''
        #d['Iambic'] = self.isIambic(text)
        #d[text[-1]] += 1
        #print kTOKENIZER.tokenize(text)
        for ii in words:
            d[morphy_stem(ii)] += 1
            if ii not in string.punctuation:
                d['syllables'] += self.num_syllables(ii)
            d['char_count'] += len(ii)
        #print d
        return d
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--trainfile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input train file")
    parser.add_argument("--testfile", "-t", nargs='?', type=argparse.FileType('r'), default=None, help="input test file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")
    parser.add_argument('--subsample', type=float, default=1.0,
                        help='subsample this fraction of total')
    args = parser.parse_args()
    trainfile = prepfile(args.trainfile, 'r')
    if args.testfile is not None:
        testfile = prepfile(args.testfile, 'r')
    else:
        testfile = None
    outfile = prepfile(args.outfile, 'w')

    # Create feature extractor (you may want to modify this)
    fe = FeatureExtractor()
    
    # Read in training data
    train = DictReader(trainfile, delimiter='\t')
    
    # Split off dev section
    dev_train = []
    dev_test = []
    full_train = []

    for ii in train:
        if args.subsample < 1.0 and int(ii['id']) % 100 > 100 * args.subsample:
            continue
        feat = fe.features(ii['text'])
        #print feat
        if int(ii['id']) % 5 == 0:
            dev_test.append((feat, ii['cat']))
            #print dev_test
        else:
            dev_train.append((feat, ii['cat']))
            #print dev_train
        full_train.append((feat, ii['cat']))

    # Train a classifier
    sys.stderr.write("Training classifier ...\n")
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train)

    right = 0
    total = len(dev_test)
    for ii in dev_test:
        prediction = classifier.classify(ii[0])
        if prediction == ii[1]:
            right += 1
    sys.stderr.write("Accuracy on dev: %f\n" % (float(right) / float(total)))

    if testfile is None:
        sys.stderr.write("No test file passed; stopping.\n")
    else:
        # Retrain on all data
        classifier = nltk.classify.NaiveBayesClassifier.train(dev_train + dev_test)

        # Read in test section
        test = {}
        for ii in DictReader(testfile, delimiter='\t'):
            test[ii['id']] = classifier.classify(fe.features(ii['text']))

        # Write predictions
        o = DictWriter(outfile, ['id', 'pred'])
        o.writeheader()
        for ii in sorted(test):
            o.writerow({'id': ii, 'pred': test[ii]})
