import tweetThread as TM
import pickle
import lsh
import tweet as T
from time import sleep
from collections import defaultdict
from football_subevent_classifier import FootballRecognizer
import sys

SIM_THRESHOLD = 0.6

recognizer = FootballRecognizer()
recognizer.start()

tweet_thread_manager = TM.TweetThreadManager(max_values_per_thread=40,
											 old_thread_secs=60,
											 post_rate=4.0,
											 recognizer=recognizer)
tweet_thread_manager.start()

sample_vect = 'vect_with_sample'
given_vect = 'vect_with_given'
vect_to_use = given_vect

with open(vect_to_use) as f:
	vect = pickle.load(f)

bucket_set = lsh.BucketSet(l=10,
						   k=13,
						   num_features=len(vect.get_feature_names()),
						   max_values=40)

tweet_freqs = defaultdict(int)

for tweet in T.raw_tweets_to_dict(sys.stdin):

	doc = T.process_text_from_tweet(tweet)

	tweet_freqs[tweet.get('created_at')] += 1
	
	trans = vect.transform([doc])
	num_matched_terms = len(trans.indices)

	if num_matched_terms < 2:
		continue

	tweetV = T.TweetVect(tweet=tweet, vect=trans.toarray()[0])

	nearest_neighbour = bucket_set.get_nearest_neighbour(tweetV)

	if nearest_neighbour and nearest_neighbour[0] < SIM_THRESHOLD:
		tweet_thread_manager.add_tweet_vect(tweetV, nearest_neighbour[1])

sleep(5)
tweet_thread_manager.stop()
tweet_thread_manager.print_stats()
;recognizer.stop()
