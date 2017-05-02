
import re
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

def makeGuess(dvwld):
    guessLength = (len(dvwld)+1)
    #return [Counter({'': 3})]*guessLength # ~63.5%
    with open("testin.txt", 'r') as f: # ~42.7 - 63.5
        fulltext = f.read()
    return([Counter(makeAnswerKey(fulltext))]*guessLength)

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

def grade(answer, guess):
    assert(len(answer) == len(guess))
    score = 0
    for i, vowelSequence in enumerate(answer):
        letterCounter = guess[i]
        if (letterCounter.most_common(1))[0][0]== vowelSequence:
            score +=1
        #if vowelSequence in letterCounter:
        #    score += float(letterCounter[vowelSequence])/sum(letterCounter.values())
        else:
            score += 0
    return (score, len(answer))

def runtests(text):
    teststings = ['toot','The quick Brown Fox jumps over the Lazy Dog. Verily! Forsooth.']
    for test in teststings:
        if DEBUG:
            print revowel(makeAnswerKey(test), disemvowel(test))
        assert(revowel(makeAnswerKey(test), disemvowel(test))==test)

def gradetrip(text):
    correct, total = grade(makeAnswerKey(text), makeGuess(disemvowel(text)))
    print str(correct) +'/'+ str(total) +  ' = ' +  str(float(correct)/total)

def main():
    with open ('testin.txt', 'r') as f:
        fulltext = f.read()
        runtests(fulltext)
        gradetrip(fulltext)



if __name__ == '__main__':
    main()


#wordlist is from http://www-01.sil.org/linguistics/wordlists/english/

#Results with vowel to star ('*'): Counter({'1': 88470, '2': 6998, '3': 1514, '4': 411, '5': 123, '6': 34, '7': 9, '8': 5, '9': 1})
#results with vowel to null ('') : Counter({'1': 63700, '2': 8938, '3': 2606, '4': 1134, '5': 631, '6': 372, '7': 220, '8': 139, '9': 130, '10': 88, '11': 58, '12': 54, '13': 44, '15': 37, '14': 33, '16': 21, '21': 16, '17': 16, '19': 15, '18': 15, '20': 14, '22': 7, '25': 6, '23': 5, '27': 4, '26': 3, '24': 2, '28': 2, '29': 2, '44': 1, '38': 1, '31': 1, '30': 1})
