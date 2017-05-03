
import re
#import nltk
from collections import Counter

def disemvowel(s):
    return re.sub('[AEIOUaeiou]', '*',s)

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
    #This will eventually have to deal with correcting while preserving punctuation, capitalization, etc.
    with open (filein, 'r') as f:
        text = revowel(disemvowel(f.read()))
        with open(fileout, 'w') as o:
            o.write(text)
def main():
    revowel('* l*k*')
    #print revowel(disemvowel('Hello World!'))
    #roundtrip('gatsby.txt', 'daisy.txt')
'''
#just messing around
    for key in d:
        l = len(d[key])
        if l>7:
            print key + ''.join(d[key]) # Q: why printing on separate lines?
    print Counter([str(len(d[key])) for key in d])
'''

if __name__ == '__main__':
    main()


#wordlist is from http://www-01.sil.org/linguistics/wordlists/english/

#Results with vowel to star ('*'): Counter({'1': 88470, '2': 6998, '3': 1514, '4': 411, '5': 123, '6': 34, '7': 9, '8': 5, '9': 1})
#results with vowel to null ('') : Counter({'1': 63700, '2': 8938, '3': 2606, '4': 1134, '5': 631, '6': 372, '7': 220, '8': 139, '9': 130, '10': 88, '11': 58, '12': 54, '13': 44, '15': 37, '14': 33, '16': 21, '21': 16, '17': 16, '19': 15, '18': 15, '20': 14, '22': 7, '25': 6, '23': 5, '27': 4, '26': 3, '24': 2, '28': 2, '29': 2, '44': 1, '38': 1, '31': 1, '30': 1})
