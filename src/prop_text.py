import json
from pprint import pprint
import pandas as pd
import arrow
import re
import json

from nltk.corpus import stopwords
import multiprocessing
import _pickle as Pickle
from gensim.models import Word2Vec
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV, cross_validate, train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, normalize
from datetime import datetime
from nltk.stem import PorterStemmer, LancasterStemmer, SnowballStemmer

from spellCheck2s import correction, replace_typical_misspell

from emoji import UNICODE_EMOJI

def is_emoji(s):
    count = 0
    for emoji in UNICODE_EMOJI:
        count += s.count(emoji)
        if count > 1:
            return False
    return bool(count)

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

import spacy
        
nlp_v = spacy.load('en_core_web_lg')
def emb(doc, nlp = nlp_v): 
    return nlp(doc).vector

nlp = spacy.load('en') # import spacy, load model
def noun_notnoun(phrase, nlp=nlp):
    doc = nlp(phrase) # create spacy object
    token_not_noun = []
    notnoun_noun_list = []

    for item in doc:
        if item.pos_ != "NOUN": # separate nouns and not nouns
            token_not_noun.append(item.text)
        if item.pos_ == "NOUN":
            noun = item.text

    for notnoun in token_not_noun:
        notnoun_noun_list.append(notnoun + " " + noun)

    return notnoun_noun_list

def textprep(doc, tokenize = False, bySentence = False, sws = set(stopwords.words('english'))): # TODO by sent
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from bs4 import BeautifulSoup
    from nltk.tokenize import word_tokenize  
    import string
    
    punc = string.punctuation 
    lemmatizer = WordNetLemmatizer()
    # stemmer=SnowballStemmer("english")
    remove_punc = lambda s: re.sub(f'[{punc}]+', '', s)
    remove_html = lambda s: re.sub(r'https?:\/\/.*[\r\n]*', '', s, flags=re.MULTILINE) 
    #BeautifulSoup(s,'html.parser').get_text()
    remove_sw = lambda arr: [x for x in arr if x not in sws]

    # clean - emoji, punc, html
    doc = doc.reaplace('/', ' ')
    doc = replace_typical_misspell(doc)
    doc = deEmojify(doc)
    doc = remove_html(doc)
    doc = doc.lower()
    doc = remove_punc(doc)
    
    # tokenize, remove sws, lemmizate, spelling correction
    doc = word_tokenize(doc)
    doc = remove_sw(doc)
    doc = [lemmatizer.lemmatize(word) for word in doc]
    doc = [correction(word) for word in doc]
    
    # return 
    if tokenize == True:
        return doc
    else:
        return ' '.join(doc)

"""
1) clean data with textprep 
2) two word2vec file: 1 vs bigram
3) save df and vector separately
"""

sws = set(stopwords.words('english'))
sws.remove('no') 
s="ith the release date of November 18, 2115 I don't think none of us has the chance of seeing this film"
x = textprep(s, sws=sws)
print(x)
    # eng_stopwords = set(stopwords.words('english'))
    # from multiprocessing import Pool
    # import _pickle as Pickle
    # for yr in [2018, 2019]:
    #     df = pd.read_csv(f'comments{yr}final_all.csv')
    #     pool = Pool(32)

    #     df.body_clean = df.body_clean.astype(str)
    #     df['body_vec'] = pool.map(emb, df.body_clean.values)
    #     Pickle.dump(df.body_vec.values, open(f'comment{yr}vec.p', 'wb'))
    #     pool.close()
    #     pool.join()
