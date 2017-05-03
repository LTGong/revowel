
import re
import sys
import pickle
#import nltk
from collections import Counter

DEBUG = False

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

import nltk

def compile_word_frequencies(corpus_text):
    res = {}
    #words = nltk.Text(nltk.word_tokenize(corpus_text
    #for word in words:
    r"([B-DF-HJ-NP-TV-XZb-df-hj-np-tv-xz]+'?[B-DF-HJ-NP-TV-XZb-df-hj-np-tv-xz]*)"
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

def generate_trigram_model(fulltext = "training.txt"):
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

    with open('trigram.pickle', 'wb') as f:
        pickle.dump(model, f, pickle.HIGHEST_PROTOCOL)

def use_trigram_model(dvwld):
    #guessLength = (len(dvwld)+1)
    with open('trigram.pickle', 'rb') as f:
        cons_lookup = pickle.load(f)
    n_consonants_sampled = 2
    guess = [Counter()]# first vowel not in model, we punt (correct for fencepost)
    for i in range(len(dvwld)-n_consonants_sampled+1):
        cons = dvwld[i:i+n_consonants_sampled]
        #print dvwld[i] + repr(cons_lookup[cons]) + dvwld[i+1]
        if cons in cons_lookup:
            guess += [cons_lookup[cons]]
        else:
            guess += [Counter()]
    guess += [Counter()] #again correct for fencepost at end.
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

def use_word_model(dvwld):
    for char in dvwld:
        pass
        #TK
    '''
    guessLength = (len(dvwld)+1)
    with open('word.pickle', 'rb') as f:
        cons_lookup = pickle.load(f)
    n_consonants_sampled = 2
    guess = [Counter()]# first vowel not in model, we punt (correct for fencepost)
    for i in range(len(dvwld)-n_consonants_sampled+1):
        cons = dvwld[i:i+n_consonants_sampled]
        #print dvwld[i] + repr(cons_lookup[cons]) + dvwld[i+1]
        if cons in cons_lookup:
            guess += [cons_lookup[cons]]
        else:
            guess += [Counter()]
    guess += [Counter()] #again correct for fencepost at end.
    '''
    return guess

def generate_models(filename = "training.txt"):
    '''Make (and save) models as pickles TODO: timing, sizing'''
    with open(filename, 'r') as f:
        fulltext = f.read()
    generate_trigram_model(fulltext)

def makeGuess(dvwld):
    return use_trigram_model(dvwld)

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
    key.append('')
    assert (len(key) == len(disemvowel(voweledString))+1)
    return key #(end for fencepost)

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
        if (len(dist.most_common(1)) == 0):
            res += ['*']
        else:
            res += [dist.most_common(1)[0][0]]
    return res

#TODO refactor so 1 version grades distribution, and other compares like types (lists of vowels.)
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

def grade_dist(answer, dist_guess):
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

def gradetrip(text):
    dvwld = disemvowel(text)
    topVowels = get_top_vowels(makeGuess(dvwld))
    correct, total = grade(makeAnswerKey(text),topVowels)
    abstentions = len(disemvowel(text))-1-total
    print str(correct) +'/'+ str(total) +  ' = ' +  str(float(correct)/total) + ' no guess for ' + str(abstentions)
    print revowel(topVowels, dvwld)[:100]

def main():
    with open ('testin.txt', 'r') as f:
        fulltext = f.read()
        runtests(fulltext)
        gradetrip(fulltext)



#generate_trigram_model("Hello World!")
#use_trigram_model(disemvowel("Hello World!"))

if __name__ == '__main__':
    generate_models()
    main()
    #dg()
    #test_models(evaluator)

    '''
    print sys.argv
    print len(sys.argv)
    if (len(sys.argv)>1 and sys.argv[1] == '-train' or sys.argv[1] == '-t' ):
        print('yup')
    else:
        main()
    '''


#wordlist is from http://www-01.sil.org/linguistics/wordlists/english/

#Results with vowel to star ('*'): Counter({'1': 88470, '2': 6998, '3': 1514, '4': 411, '5': 123, '6': 34, '7': 9, '8': 5, '9': 1})
#results with vowel to null ('') : Counter({'1': 63700, '2': 8938, '3': 2606, '4': 1134, '5': 631, '6': 372, '7': 220, '8': 139, '9': 130, '10': 88, '11': 58, '12': 54, '13': 44, '15': 37, '14': 33, '16': 21, '21': 16, '17': 16, '19': 15, '18': 15, '20': 14, '22': 7, '25': 6, '23': 5, '27': 4, '26': 3, '24': 2, '28': 2, '29': 2, '44': 1, '38': 1, '31': 1, '30': 1})
