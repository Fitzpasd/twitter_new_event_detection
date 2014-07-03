import sys
import pickle
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords as SW

PERCENT_OF_VOCAB = 0.005

def get_vocab_from_freq_dict(freq_dict, size):
	sorted_freqs = sorted([(freq, word) 
							for word, freq in freq_dict.iteritems()], 
							reverse=True)

	return [word for freq, word in sorted_freqs[:size]]

	
with open('football_term_freq.json') as f:
	freq_dict = json.load(f)

vocab_size = int(len(freq_dict) * PERCENT_OF_VOCAB)
sample_full_vocab = get_vocab_from_freq_dict(freq_dict, vocab_size)

stopwords = SW.words('english')

vect = TfidfVectorizer(sublinear_tf=True, 
					   analyzer='word',
					   stop_words=stopwords,
					   vocabulary=sample_full_vocab)

vect.fit(sys.stdin)

with open('vect_with_sample', 'w') as f:
	pickle.dump(vect, f)
