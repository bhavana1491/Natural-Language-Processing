#!/bin/python
import re
from nltk.stem.porter import *
f_Name = set()
l_Name = set()
tv_set = set()
stop_set = set()
county_set = set()
sportsl_set = set()
sportst_set = set()
month_set = set(["january","february","march","april","may","june","july","august","september","october","november","december","jan","feb","mar","apr","jun","jul","aug","sept","oct","nov","dec","sep"])
prep_set = set(["in", "to", "from", "across", "around", "at", "for", "by"])
consumer_set = set()
venture_set = set()
def preprocess_corpus(train_sents):
    fNameF = open('./data/lexicon/firstname.5k','r')
    lNameF = open('./data/lexicon/lastname.5000','r')
    fName = fNameF.read().splitlines()
    fName = map(str.lower,fName)
    lName = lNameF.read().splitlines()
    lName = map(str.lower, lName)
    global f_Name,l_Name
    f_Name = set(fName)
    l_Name = set(lName)
    #print f_Name
    #print l_Name
    tvF = open('./data/lexicon/tv.tv_program','r')
    tvL = tvF.read().splitlines()
    tvL = map(str.lower,tvL)
    global tv_set
    tv_set = set(tvL)

    stopF = open('./data/lexicon/english.stop','r')
    stopL = stopF.read().splitlines()
    stopL = map(str.lower,stopL)
    global stop_set
    stop_set = set(stopL)

    countyF = open('./data/lexicon/location.country','r')
    countyL = countyF.read().splitlines()
    countyL = map(str.lower, countyL)
    global county_set
    county_set = set(countyL)

    sportslF = open('./data/lexicon/sports.sports_league','r')
    sportslL = sportslF.read().split()
    sportslL = map(str.lower, sportslL)
    global sportsl_set
    sportsl_set = set(sportslL)

    sportstF = open('./data/lexicon/sports.sports_team','r')
    sportstL = sportstF.read().split()
    sportstL = map(str.lower, sportstL)
    global sportst_set
    sportst_set = set(sportstL)

    ventureF = open('./data/lexicon/venture_capital.venture_funded_company','r')
    ventureL = ventureF.read().split()
    ventureL = map(str.lower, ventureL)
    global venture_set
    venture_set = set(ventureL)

    consumerF = open('./data/lexicon/business.consumer_company','r')
    consumerL = consumerF.read().split()
    consumerL = map(str.lower, consumerL)
    global consumer_set
    consumer_set = set(consumerL)

    """Use the sentences to do whatever preprocessing you think is suitable,
    such as counts, keeping track of rare features/words to remove, matches to lexicons,
    loading files, and so on. Avoid doing any of this in token2features, since
    that will be called on every token of every sentence.

    Of course, this is an optional function.

    Note that you can also call token2features here to aggregate feature counts, etc.
    """
    pass

def token2features(sent, i, add_neighs = True):
    """Compute the features of a token.

    All the features are boolean, i.e. they appear or they do not. For the token,
    you have to return a set of strings that represent the features that *fire*
    for the token. See the code below.

    The token is at position i, and the rest of the sentence is provided as well.
    Try to make this efficient, since it is called on every token.

    One thing to note is that it is only called once per token, i.e. we do not call
    this function in the inner loops of training. So if your training is slow, it's
    not because of how long it's taking to run this code. That said, if your number
    of features is quite large, that will cause slowdowns for sure.

    add_neighs is a parameter that allows us to use this function itself in order to
    recursively add the same features, as computed for the neighbors. Of course, we do
    not want to recurse on the neighbors again, and then it is set to False (see code).
    """

    ftrs = []
    # bias
    ftrs.append("BIAS")
    # position features
    if i == 0:
        ftrs.append("SENT_BEGIN")
    if i == len(sent)-1:
        ftrs.append("SENT_END")

    # the word itself
    stemmer = PorterStemmer()
    word = unicode(sent[i])
    ftrs.append("WORD=" + stemmer.stem(word.lower()))
    ftrs.append("LCASE=" + word.lower())
    # some features of the word
    if word.isalnum():
        ftrs.append("IS_ALNUM")
    if word.isnumeric():
        ftrs.append("IS_NUMERIC")
    if word.isdigit():
        ftrs.append("IS_DIGIT")
    if word.islower():
        ftrs.append("IS_LOWER")
    shape = ""
    for c in word:
        if c.isupper():
            shape += "X"
        else:
            shape += "x"
        ftrs.append("SHAPE_" + shape)

    if re.match(r'[0-9][0-9]', word):
        ftrs.append('IS_TWO_DIGIT')

    if word.lower() in month_set:
        ftrs.append("IS_MONTH")
    if word.lower().startswith("http"):
        ftrs.append("IS_URL")
    if i > 0 and word[0].isupper() and sent[i - 1] in ["in", "to", "from", "across", "around", "at", "for", "by"]:
        ftrs.append("PREV_WORD_IS_PREP")
    if len(word) > 2:
        ftrs.append("IS_PREFIX_"+ word[0:2].upper())
        ftrs.append("IS_SUFFIX_"+ word[-2:].upper())
    if len(word) >3:
        ftrs.append("IS_PREFIX_" + word[0:3].upper())
        ftrs.append("IS_SUFFIX_" + word[-3:].upper())
    # if re.match(r'[.,;:?!-+\'"]', word):
    #     ftrs.append('IS_PUNCTUATION')


    if word.lower() not in stop_set:
        if '-' in word:
            ftrs.append("IS_HYPHEN")
            hs = word.split('-')
            ftrs.append("SUB_TEXT" + hs[0].upper() + hs[1].upper())
        if word[0] is "@":
            ftrs.append("IS_FIRST_AT")
        if word[0] is "#":
            ftrs.append("IS_HASH")
        if word.isupper():
            ftrs.append("IS_UPPER")
        if word.lower() in f_Name:
            ftrs.append("IS_FNAME")
        if word.lower() in l_Name:
            ftrs.append("IS_LNAME")
        if word[0].isupper():
            ftrs.append("IS_CAPITALIZED")
        # if word[0].isupper() and word[1:].islower():
        #     ftrs.append("IS_SHAPE_Xxx")
        # if sent[i].lower() in tv_set:
        #     ftrs.append("IS_TV_SHOW")
        # else:
        if i > 0:
            s = sent[i-1] + " " + sent[i]
            if s.lower() in tv_set:
                ftrs.append("IS_TV_SHOW")
        if i < len(sent)-1:
                s = sent[i] + " " + sent[i+1]
                if s.lower() in tv_set:
                    ftrs.append("IS_TV_SHOW")
        if i > 1:
            s = sent[i-2] + " " + sent[i-1]+ " " + sent[i]
            if s.lower() in tv_set:
                ftrs.append("IS_TV_SHOW")
        if i < len(sent) - 2:
            s = sent[i] + " " + sent[i+1]+ " " + sent[i+2]
            if s.lower() in tv_set:
                ftrs.append("IS_TV_SHOW")


        if word.lower() in county_set:
            ftrs.append("IS_COUNTRY")
        else:
            if i < len(sent) - 1:
                s = sent[i] + " " + sent[i + 1]
                if s.lower() in county_set:
                    ftrs.append("IS_COUNTRY")
            if i > 0:
                s = sent[i - 1] + " " + sent[i]
                if s.lower() in county_set:
                    ftrs.append("IS_COUNTRY")
            # if i > 1:
            #     s = sent[i-2] + " " + sent[i-1]+ " " + sent[i]
            #     if s.lower() in county_set:
            #         ftrs.append("IS_COUNTRY")
            # if i < len(sent) - 2:
            #     s = sent[i] + " " + sent[i+1]+ " " + sent[i+2]
            #     if s.lower() in county_set:
            #         ftrs.append("IS_COUNTRY")

        if word.lower() in sportsl_set or word.lower() in sportst_set:
            ftrs.append("IS_SPORTS")

        if word.lower() in venture_set or word.lower() in consumer_set:
            ftrs.append("IS_COMPANY")
    # previous/next word feats
    if add_neighs:
        if i > 0:
            for pf in token2features(sent, i-1, add_neighs = False):
                ftrs.append("PREV_" + pf)
        if i < len(sent)-1:
            for pf in token2features(sent, i+1, add_neighs = False):
                ftrs.append("NEXT_" + pf)

    # return it!
    # if "PREV_IS_FNAME" in ftrs and "IS_LNAME" in ftrs:
    #     ftrs.append("CL_NAME")
    if "PREV_IS_SPORTS" in ftrs and "IS_SPORTS" in ftrs:
        ftrs.append("CL_SPORTS")

    if "IS_SPORTS" in ftrs and "NEXT_IS_SPORTS" in ftrs:
        ftrs.append("CL_SPORTS")

    # if "PREV_IS_TWO_DIGIT" in ftrs and "IS_MONTH" in ftrs:
    #     ftrs.append("IS_DATE")
    #
    # if "IS_MONTH" in ftrs and "NEXT_IS_TWO_DIGIT" in ftrs:
    #     ftrs.append("IS_DATE")
    #
    # if "PREV_IS_MONTH" in ftrs and "IS_TWO_DIGIT" in ftrs:
    #     ftrs.append("IS_DATE")
    #
    # if "IS_TWO_DIGIT" in ftrs and "NEXT_IS_MONTH" in ftrs:
    #     ftrs.append("IS_DATE")


    # if "PREV_IS_SHAPE_Xxx" in ftrs and "IS_SHAPE_Xxx" in ftrs:
    #     ftrs.append("CL_SHAPE")
    # if "IS_SHAPE_Xxx" in ftrs and "NEXT_IS_SHAPE_Xxx" in ftrs:
    #     ftrs.append("CL_SHAPE")
    return ftrs

if __name__ == "__main__":
    sents = [
    [ "I", "love", "food" ],["I","Like","Irish","Whiskey"],["Patricia","Adam","Smith"]
    ]
    preprocess_corpus(sents)
    for sent in sents:
        for i in xrange(len(sent)):
            print sent[i], ":", token2features(sent, i)
