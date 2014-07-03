import sys
import football_subevent_classifier as FC
import ast
import tweet as T
from collections import defaultdict
from sliding_window import *
from time import sleep
from threading import Lock
import json
from datetime import datetime, timedelta
import pickle

def get_post_rates(tweet_freqs, t):
	sorted_freqs = sorted([(k,v) for k,v in tweet_freqs.iteritems()])
	one_second = timedelta(seconds=1)
	intervals = [10,20,30,60]
	res = []

	for k, v in sorted_freqs:
		dt = T.datetime_from_tweet_created_at(k)
		window_end = dt - one_second

		for interval in intervals:
			window = get_window_of_sorted_freqs(sorted_freqs, 
												interval, 
												window_end)

			window_length = len(window)

			if window_length is not interval:
				continue

			if post_rate(window) > t:
				dt = window[int(window_length / 2)][0]
				res.append(dt)
				break

	return set(res)

tweet_freqs = defaultdict(int)
tweets_per_time = defaultdict(list)

with open('vect_with_given') as f:
	vect = pickle.load(f)

for tweet in T.raw_tweets_to_dict(sys.stdin):
	doc = T.process_text_from_tweet(tweet)

	timestamp = tweet.get('created_at')

	tweet_freqs[timestamp] += 1

	l = tweets_per_time[timestamp]
	l.append(tweet)

event_times = get_post_rates(tweet_freqs, 1.7)	

for dt in event_times:
	time_str = dt.strftime('%a %b %d %H:%M:%S +0000 %Y')

	event_tweets = tweets_per_time.get(time_str)

	texts = [e.get('text') for e in event_tweets]

	event = FC.classify_list(texts)
	if event :
		print '%s - %s' % (time_str, FC.STR_MAP[e])
		print '\n'.join(texts)
