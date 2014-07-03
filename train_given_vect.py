import sys
import pickle
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords as SW

with open('football_terms.txt') as f:
	vocab = [term.replace('\n', '') for term in f.readlines()]
	
with open('football_teams.txt') as f:
	for line in f:
		vocab.append(line.replace('\n', ''))

stopwords = SW.words('english')

max_n = max([len(phrase.split()) for phrase in vocab])

vect = TfidfVectorizer(sublinear_tf=True, 
					   analyzer='word',
					   stop_words=stopwords,
					   ngram_range=(1,max_n),
					   vocabulary=vocab)

vect.fit(sys.stdin)

with open('vect_with_given', 'w') as f:
	pickle.dump(vect, f)
