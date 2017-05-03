
import re, random, string
import sys
import pickle
#import nltk
from collections import Counter

DEBUG = False
NO_GUESS = "#No Guess#"

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
            res[key][word]+=1
        else:
            res[key] = Counter({word:1})
    with open('word_freq.pickle', 'wb') as f:
        pickle.dump(res, f, pickle.HIGHEST_PROTOCOL)



def generate_unigram_model(fulltext = "training.txt"):
    model = Counter(makeAnswerKey(fulltext))
    #print(repr(model))
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


def dists_from_word_model(dvwld):
    segments = segment(dvwld)
    if type(segments[0]) is int:
        segments[0] +=1
    if type(segments[-1]) is int:
        segments[-1] +=1
    with open('word_freq.pickle', 'r') as f:
        wordDist = pickle.load(f)
        likeliest_words = {k:v.most_common(1)[0][0] for k, v in wordDist.iteritems()}

    res = []
    for sequence in segments:
        if type(sequence) is int:
            res += [NO_GUESS]*(sequence-1)
        else:
            if sequence in likeliest_words:
                vowels = makeAnswerKey(likeliest_words[sequence])
                if type(vowels) is str:
                    print vowels
                res += [Counter({s:1}) for s in makeAnswerKey(likeliest_words[sequence])]
            else:
                res+=[NO_GUESS]*(len(sequence)+1)
    return res


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
    if len(vowel_pen):
        key.append(vowel_pen)
    else:
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
            if type(dist) is str:
                print dist
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
    abstentions = len(disemvowel(text))-total
    print "Right: "+ str(correct) +"  Wrong: "+ str(total-correct) +  " Correct of taken " + str(float(correct)/total)[:4]+ " Correct of all " + str(float(correct)/(total+abstentions))[:4] + ' (' + str(abstentions) + " omitted)"

    guess_text = revowel(topVowels, dvwld)

def generate_models(filename = "training.txt"):
    '''Make (and save) models as pickles TODO: timing, sizing'''
    with open(filename, 'r') as f:
        fulltext = f.read()
    for i in range(1, 6):
        generate_Ngram_model(fulltext, i)
    generate_word_model(fulltext)

def entropy(dist_counter):
    pass

def max_entropy(dist_counter):
    print '.',

def normalize_dist(dist):
    res = {}
    size = sum(dist.itervalues())
    for i, c, in dist.most_common():
        res[i] = float(c)/size

def backoff(candidate_dists):
    res = []
    for dist in candidate_dists:
        if dist != NO_GUESS:
            return dist
    #where to find the ones that no method gets?
    return NO_GUESS

def weighted_avg(candidate_dists):
    pass

def degenerate_best(candidate_dists):
    return candidate_dists[0]

#TK - broken
def mushed(candidate_dists):
    realdists = [elm for elm in candidate_dists if isinstance(candidate_dists,type(Counter()))]
    if len(realdists):
        print '.',
        return sum(realdists,Counter())
    return NO_GUESS

def reconcile(candidate_dists):
    #weighted_avg(candidate_dists)
    #return most preferable of candidate distributions.
    return backoff(candidate_dists)
    #return weighted_avg(candidate_dists)
    #return mushed(candidate_dists)
    #return max_entropy(candidate_dists)


def nums():
    with open ('testin.txt', 'r') as f:
        fulltext = f.read()
        runtests(fulltext)
        gradetrip(fulltext)
def sample():
    with open('demo.txt', 'r') as f:
        text = f.read()
        dvwld = disemvowel(text)
        print revowel(get_top_vowels(gen_dists(dvwld)), dvwld)

def gen_dists(dvwld):
    ordered_dist_sequences = [dists_from_word_model(dvwld)] + [dists_from_Ngrams(dvwld, i) for i in reversed(range(1,6))]
    res = [reconcile(vowel_candidates) for vowel_candidates in zip(*ordered_dist_sequences)]
    #res = dists_from_word_model(dvwld)
    return res

def reconcile(candidate_dists):
    #weighted_avg(candidate_dists)
    #return most preferable of candidate distributions.
    return backoff(candidate_dists)
    #return weighted_avg(candidate_dists)
    #return mushed(candidate_dists)
    #return max_entropy(candidate_dists)

def evaluate():
    nums()
    sample()

if __name__ == '__main__':
    #generate_models()
    evaluate()
