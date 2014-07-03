from collections import defaultdict
from datetime import datetime, timedelta
from time import sleep
import itertools
import tweet
import threading

import football_subevent_classifier as FC
import sliding_window as SW

class TweetThreadManager(threading.Thread):
	def __init__(self, max_values_per_thread, old_thread_secs, post_rate, recognizer):
		super(TweetThreadManager, self).__init__()
		self.tweet_threads = []
		self.max_values_per_thread = max_values_per_thread
		self.old_thread_secs = old_thread_secs
		self.running = True
		self.add_queue = []
		self.post_rate = post_rate
		self.recognizer = recognizer
		self.num_created, self.num_deleted = 0, 0

	def run(self):
		one_second = timedelta(seconds=1)

		while self.running:
			wake_time = datetime.now() + one_second
	
			self.clear_add_queue()
			self.delete_old_threads()
			self.detect_events()

			sleep_seconds = (wake_time - datetime.now()).total_seconds()
			if sleep_seconds > 0:
				sleep(sleep_seconds)

	def stop(self):
		self.running = False

	def add_tweet_thread(self, tweet_thread):
		self.tweet_threads.append(tweet_thread)

	def add_tweet_vect(self, tweet_vect, nearest_neighbour):
		self.add_queue.append((tweet_vect, nearest_neighbour))

	def clear_add_queue(self):
		for tweet_vect, nearest_neighbour in self.add_queue:
			create_new = True

			for t in self.tweet_threads:
				if t.has_tweet_vect(nearest_neighbour):
					t.add_tweet_vect(tweet_vect)
					create_new = False
					break

			if create_new:
				new_thread = self.create_new_thread(self.max_values_per_thread, 
													tweet_vect, 
													nearest_neighbour)
				self.tweet_threads.append(new_thread)

		del self.add_queue[:]

	def create_new_thread(self, max_values, *tweet_vects):
		self.num_created += 1
		new_thread = TweetThread(max_values)

		for tv in tweet_vects:
			new_thread.add_tweet_vect(tv)

		return new_thread
	
	def delete_old_threads(self):
		for thread in self.tweet_threads:
			if thread.get_age_seconds() > self.old_thread_secs:
				self.num_deleted += 1
				self.tweet_threads.remove(thread)

	def detect_events(self):
		for thread in self.tweet_threads:
			p = thread.get_post_rate()
			if p > self.post_rate: 
				self.recognizer.recognize_thread(thread)
				self.tweet_threads.remove(thread)

	def print_stats(self):
		print '---------Cluster Manager------------------'
		print 'Number of clusters created = %d' % self.num_created
		print 'Number of clusters deleted = %d' % self.num_deleted
		print 'Number of clusters currently = %d' % len(self.tweet_threads)
		for t in self.tweet_threads:
			'__________Cluster_____________'
			t.print_stats()
			'_____________________________'
		print '------------------------------------------'

class TweetThread:
	def __init__(self, max_values):
		self.frequencies = defaultdict(int)
		self.tweet_vects = {}
		self.overflow_tweets = {}
		self.max_values = max_values

	def add_tweet_vect(self, tweetVect):
		timestamp = tweetVect.tweet.get('created_at')

		self.frequencies[timestamp] += 1
		
		tweet_id = tweetVect.tweet.get('id')

		if len(self.tweet_vects) < self.max_values:
			self.tweet_vects[tweet_id] = tweetVect
		else:
			self.overflow_tweets[tweet_id] = 1

	def has_tweet_vect(self, tweet_vect):
		tweet_id = tweet_vect.tweet.get('id')
		return tweet_id in self.tweet_vects or tweet_id in self.overflow_tweets

	def get_age_seconds(self):
		sorted_times = sorted([tweet.datetime_from_tweet_created_at(s)
							  for s in self.frequencies.keys()])

		return (sorted_times[-1] - sorted_times[0]).total_seconds()

	def get_timestr(self):
		sorted_freqs = sorted([s for s in self.frequencies.keys()])
		return sorted_freqs[len(sorted_freqs) /2]

	def get_post_rate(self):
		sorted_freqs = sorted([(tweet.datetime_from_tweet_created_at(k),v) 
							   for k,v in self.frequencies.iteritems()])

		if sorted_freqs[-1][0] - sorted_freqs[0][0] < timedelta(seconds=10) or len(self.tweet_vects) < 10:
			return 0

		mid_time = sorted_freqs[-1][0] - (sorted_freqs[-1][0] - sorted_freqs[0][0])

		first_half = sum([freq for time, freq in sorted_freqs if time <= mid_time])
		second_half = sum([freq for time, freq in sorted_freqs if time > mid_time])

		return float(second_half) / first_half if first_half > 0 else 0

	def get_texts(self):
		tweets = [v.tweet for k,v in self.tweet_vects.iteritems()]
		return [t.get('text').encode('utf-8') for t in tweets]

	def print_stats(self):
		a = len(self.tweet_vects)
		b = len(self.overflow_tweets)
		print 'Number of documetns = %d' % a
		print 'Number of overflow documetns = %d' % b
		print 'Number of total = %d' % (a + b)
