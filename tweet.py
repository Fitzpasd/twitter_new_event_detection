import ast
import json
import itertools
from nltk.corpus import stopwords as SW
from collections import namedtuple
import nlp
from datetime import datetime
from email.utils import parsedate_tz

TweetVect = namedtuple('TweetVect', 'tweet vect'.split())

not_a_reply = lambda x: not x.get('in_reply_to_user_id')
not_a_retweet = lambda x: not x.get('retweeted_status')
no_urls = lambda x: not x.get('entities').get('urls')
acceptable_tweet = lambda x: not_a_reply(x) and not_a_retweet(x) and no_urls(x)

def raw_tweets_to_dict(src, ast=True):
	raw_to_dict_func = raw_to_dict_ast if ast else raw_to_dict_json 
	tweet_dicts = raw_to_dict_func(src)
	
	return itertools.ifilter(acceptable_tweet, tweet_dicts)	

def raw_to_dict_ast(src):
	for raw in src:
		try:
			tweet = ast.literal_eval(raw)
			yield tweet
		except (SyntaxError, ValueError):
			continue

def raw_to_dict_json(src):
	for raw in src:
		try:
			tweet = json.loads(raw)
			yield tweet
		except (SyntaxError, ValueError):
			continue

def process_text_from_tweet(tweet_dict, as_string=False):
	text = tweet_dict.get('text')
	text = text if not as_string else unicode.encode(text, 'utf-8')
	no_mentions = nlp.remove_mentions(text)
	return nlp.remove_grammar(no_mentions)

def datetime_from_tweet(tweet):
	return datetime_from_tweet_created_at(tweet.get('created_at'))

def datetime_from_tweet_created_at(created_at):
	parsed = parsedate_tz(created_at)
	return datetime(*parsed[:6])
