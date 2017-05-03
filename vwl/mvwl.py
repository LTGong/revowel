
import re, random, string
import sys
import pickle
#import nltk
from collections import Counter

DEBUG = False
NO_GUESS = "#No Guess#"

'''

def makeDetectorDict(filename):
    with open(filename, 'r') as f:
        #below strips newlines from the ends of our strings, per http://stackoverflow.com/a/15233739
        words = [line.rstrip('\n') for line in f]
    #TK - this comes up often enough to be an idiom - does it have a "normal form"
    d={}
    for word in words:
        key = disemvowel(word)
        if key in d:
            d[key].append(word)
        else:
            d[key] = [word]
    return d


def revowel(s):
    res =[]
    d = makeDetectorDict('wordlist.txt')
    success = 0
    failure = 0
    for w in [w.lower() for w in re.findall(r'[a-zA-Z\*]+', s)]:
        print(w)
        print(d[w])
        if w in d and len(d[w])==1:
            res += d[w]
            success +=1
        else:
            res += [w]
            failure +=1
    print float(success)/(success+failure)
    return ' '.join(res)
    #currently only works for star replacement


def roundtrip(filein, fileout):
    with open (filein, 'r') as f:
        text = revowel(disemvowel(f.read()))
        with open(fileout, 'w') as o:
            o.write(text)
'''

#import nltk

def compile_word_frequencies(corpus_text):
    res = {}
    #words = nltk.Text(nltk.word_tokenize(corpus_text
    #for word in words:
    #r"([B-DF-HJ-NP-TV-XZb-df-hj-np-tv-xz]+'?[B-DF-HJ-NP-TV-XZb-df-hj-np-tv-xz]*)"
    pattern = re.compile(r'([A-Za-z]+)')
    for m in re.finditer(pattern, corpus_text):
        word =  m.group(1)
        key = disemvowel(word)
        if key in res:
            res[key]+=1
        else:
            res[key] = Counter({word:1})
    with open('word_freq.pickle', 'wb') as f:
        pickle.dump(res, f, pickle.HIGHEST_PROTOCOL)



def generate_unigram_model(fulltext = "training.txt"):
    model = Counter(makeAnswerKey(fulltext))
    print(repr(model))
    with open('unigram.pickle', 'wb') as f:
        pickle.dump(model, f, pickle.HIGHEST_PROTOCOL)

def use_unigram_model(dvwld):
    guessLength = (len(dvwld)+1)
    with open('unigram.pickle', 'rb') as f:
        return([pickle.load(f)]*guessLength)

def generate_Ngram_model(fulltext = "training.txt",n=2):
    pairs = []
    vowel_sequences = makeAnswerKey(fulltext)
    anchors = disemvowel(fulltext)
    #n = 2
    model = {}
    for i in range(len(anchors)-n+1):
        anch = anchors[i:i+n]
        vowel_seq = vowel_sequences[i+n-1]
        if anch in model:
            model[anch][vowel_seq] +=1
        else:
            model[anch] = Counter({vowel_seq:1})

    with open(str(n)+'gram.pickle', 'wb') as f:
        pickle.dump(model, f, pickle.HIGHEST_PROTOCOL)

def dists_from_Ngrams(dvwld, n = 2):
    #guessLength = (len(dvwld)+1)
    with open(str(n)+'gram.pickle', 'rb') as f:
        cons_lookup = pickle.load(f)
    ##n = 2
    guess = [NO_GUESS]*(n-1)# first vowel not in model, we punt (correct for fencepost)
    for i in range(len(dvwld)-n+1):
        cons = dvwld[i:i+n]
        #print dvwld[i] + repr(cons_lookup[cons]) + dvwld[i+1]
        if cons in cons_lookup:
            guess += [cons_lookup[cons]]
        else:
            guess += [NO_GUESS]
    guess += [NO_GUESS]#again correct for fencepost at end.
    return guess

def generate_word_model(fulltext):
    compile_word_frequencies(fulltext)
    '''
    pairs = []
    vowel_sequences = makeAnswerKey(fulltext)
    anchors = disemvowel(fulltext)
    n_consonants_sampled = 2
    model = {}
    for i in range(len(anchors)-n_consonants_sampled+1):
        anch = anchors[i:i+n_consonants_sampled]
        vowel_seq = vowel_sequences[i+n_consonants_sampled-1]
        if anch in model:
            model[anch][vowel_seq] +=1
        else:
            model[anch] = Counter({vowel_seq:1})

    with open('word.pickle', 'wb') as f:
        pickle.dump(model, f, pickle.HIGHEST_PROTOCOL)
    '''

def dists_from_word(dvwld):
    segments = segment(dvwld)
    if type(segments[0]) is int:
        segments[0] +=1
    if type(segments[-1]) is int:
        segments[-1] +=1



def segment(dvwld):
    #consonant_letters = set(string.ascii_letters()) - set('AEIOUaeiou')
    res = []
    cons_cluster = ''
    gap_length = 0
    for char in dvwld:
        if (char in string.ascii_letters):#consonant_letters):
            if gap_length>0:
                res += [gap_length]
                gap_length = 0
            cons_cluster +=char
        else:
            if len(cons_cluster)>0:
                res += [cons_cluster]
                cons_cluster = ''
            gap_length  += 1
    #There's one
    if(gap_length):
        res +=[gap_length]
    else:
        res+= [cons_cluster]
    return res

def disemvowel(s):
    return re.sub('[AEIOUaeiou]', '',s)

def makeAnswerKey(voweledString):
    address = 0
    vowel_pen = ''
    key = []
    for char in voweledString:
        if char in "AEIOUaeiou":
            vowel_pen += char
        else:
            key.append(vowel_pen)
            vowel_pen = ''
    key.append('') #(end for fencepost)
    assert (len(key) == len(disemvowel(voweledString))+1)
    return key

#beware bugs! This breaks on
def revowel(vowel_arr, disemvoweled_string):
    assert(len(vowel_arr)==len(disemvoweled_string)+1)
    res = disemvoweled_string
    for i in range(1, len(disemvoweled_string)+1):
        preceding_consonents = len(disemvoweled_string)-i
        if DEBUG:
            print preceding_consonents
            print vowel_arr[preceding_consonents]
            print res[:preceding_consonents]+'_'+res[preceding_consonents:]
        res = res[:preceding_consonents]+vowel_arr[preceding_consonents]+res[preceding_consonents:]
    return res


def get_top_vowels(dist_guess):
    res = []
    for dist in dist_guess:
        if (dist == NO_GUESS):
            res += ['*']
        else:
            res += [dist.most_common(1)[0][0]]
    return res


def grade(answer, guess):
    ##assert(len(answer) == len(guess))
    n_correct = 0
    n_known_unknowns = 0

    for ans, gue in zip(answer,guess):
        if gue == '*':
            n_known_unknowns+=1
        elif ans == gue:
            n_correct +=1

    n_answered = len(answer) - n_known_unknowns
    return (n_correct, n_answered)

#TODO refactor multiplies
def partial_credit_dist(answer, dist_guess):
    assert(len(answer) == len(guess))
    n_correct = 0
    n_known_unknowns = 0
    for i, vowelSequence in enumerate(answer):
        letterCounter = guess[i]
        if (len(letterCounter.most_common(1)) == 0):
            n_known_unknowns +=1
        elif (letterCounter.most_common(1)[0][0]== vowelSequence):
            n_correct +=1
        #if vowelSequence in letterCounter:
        #    score += float(letterCounter[vowelSequence])/sum(letterCounter.values())
        else:
            n_correct += 0 #effectively "pass"
    n_answered = len(answer) - n_known_unknowns
    return (n_correct, n_answered)

def runtests(text):
    teststings = ['toot','The quick Brown Fox jumps over the Lazy Dog. Verily! Forsooth.']
    for test in teststings:
        if DEBUG:
            print revowel(makeAnswerKey(test), disemvowel(test))
        assert(revowel(makeAnswerKey(test), disemvowel(test))==test)
    #Ascertain that NO_GUESS's value didn't show up anywhere

def gradetrip(text):
    dvwld = disemvowel(text)
    topVowels = get_top_vowels(gen_dists(dvwld))
    correct, total = grade(makeAnswerKey(text),topVowels)
    abstentions = len(disemvowel(text))-1-total
    print str(correct) +'/'+ str(total) +  ' = ' +  str(float(correct)/total) + ' no guess for ' + str(abstentions)

    #sample_len = 100;
    guess_text = revowel(topVowels, dvwld)
    #sample_start = random.randint(0, len(guess_text)-sample_len)
    #print guess_text[sample_start:sample_start+sample_len]
    print guess_text[:100]

def generate_models(filename = "training.txt"):
    '''Make (and save) models as pickles TODO: timing, sizing'''
    with open(filename, 'r') as f:
        fulltext = f.read()
    generate_Ngram_model(fulltext, 1)

#This is where you would reconicile different distribution sequences.
def gen_dists(dvwld):
    return dists_from_Ngrams(dvwld, 1)

def main():
    with open ('testin.txt', 'r') as f:
        fulltext = f.read()
        runtests(fulltext)
        gradetrip(fulltext)


if __name__ == '__main__':
    generate_models()
    main()
    #dg()
    #test_models(evaluator)


#wordlist is from http://www-01.sil.org/linguistics/wordlists/english/

#Results with vowel to star ('*'): Counter({'1': 88470, '2': 6998, '3': 1514, '4': 411, '5': 123, '6': 34, '7': 9, '8': 5, '9': 1})
#results with vowel to null ('') : Counter({'1': 63700, '2': 8938, '3': 2606, '4': 1134, '5': 631, '6': 372, '7': 220, '8': 139, '9': 130, '10': 88, '11': 58, '12': 54, '13': 44, '15': 37, '14': 33, '16': 21, '21': 16, '17': 16, '19': 15, '18': 15, '20': 14, '22': 7, '25': 6, '23': 5, '27': 4, '26': 3, '24': 2, '28': 2, '29': 2, '44': 1, '38': 1, '31': 1, '30': 1})
