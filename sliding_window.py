import threading
from datetime import datetime, timedelta
from time import sleep
import tweet

class SlidingWindow(threading.Thread):
	def __init__(self, pointer_to_freqs, freqs_lock, post_rate_threshold, *time_intervals):
		super(SlidingWindow, self).__init__()
		self.pointer_to_freqs = pointer_to_freqs
		self.freqs_lock = freqs_lock
		self.post_rate_threshold = post_rate_threshold
		self.time_intervals = sorted(time_intervals)
		self.running = True

	def run(self):
		one_second = timedelta(seconds=1)

		while self.running:
			now = datetime.now()
			wake_time = now + one_second

			window_start = now - timedelta(seconds=self.time_intervals[-1])

			self.freqs_lock.acquire()
			copy_of_freqs = list([(tweet.datetime_from_tweet_created_at(k),v) 
								  for k, v in self.pointer_to_freqs.iteritems()
								  if tweet.datetime_from_tweet_created_at(k) > window_start])
			print 'len - %d' % len(copy_of_freqs)
			self.freqs_lock.release()

			if copy_of_freqs:

				for interval in self.time_intervals:
					pr, dt = post_rate_and_datetime(copy_of_freqs, interval)
					
					if pr > self.post_rate_threshold:
						i = 1
						break

			sleep_seconds = (wake_time - datetime.now()).total_seconds()
			if sleep_seconds > 0:
				sleep(sleep_seconds)

	def stop(self):
		self.running = False


def offline_sliding_window(freqs, *intervals):
	freq_list = freqs.iteritems()
	sorted_freqs = sorted(freq_list, key=lambda (k,v):k)

	for k,v in sorted_freqs:
		dt = tweet.datetime_from_tweet_created_at(k)
		for interval in intervals:
			pr, dt = post_rate_and_datetime(freq_list, interval, dt)
			if pr and dt:
				print '%d %d %d' % (interval, pr, dt)

	
def post_rate_and_datetime1(freqs, seconds, window_end):
	freqs_with_datetime = [(tweet.datetime_from_tweet_created_at(k), v)
						   for k,v in freqs]

	sorted_freqs = sorted(freqs_with_datetime, key=lambda (k,v):k)

	window = get_window(sorted_freqs, seconds, window_end)

def get_window(freqs, seconds, window_end):
	freqs_with_datetime = [(tweet.datetime_from_tweet_created_at(k), v)
						   for k,v in freqs]

	sorted_freqs = sorted(freqs_with_datetime, key=lambda (k,v):k)

	return get_window_of_sorted_freqs(sorted_freqs, seconds, window_end)

def get_window_of_sorted_freqs(freqs, seconds, window_end):
	freqs_with_datetime = [(tweet.datetime_from_tweet_created_at(k), v)
						   for k,v in freqs]

	time_interval = timedelta(seconds=seconds)

	window_start = window_end - time_interval

	return [(dt, v) for dt, v in freqs_with_datetime
		    if dt > window_start and dt <= window_end]

def post_rate(window):
	half_marker = int(len(window) / 2)
	first_half = window[:half_marker]
	second_half = window[half_marker:]

	post_rate_first = sum([v for dt, v in first_half])
	post_rate_second = sum([v for dt, v in second_half])

	if post_rate_first and post_rate_second:
		return (float(post_rate_second) / post_rate_first)
	else:
		return 0
