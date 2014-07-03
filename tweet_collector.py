from twitter import *

# Change to your keys
oauth_token = '' 
oauth_secret = ''
consumer_key = ''
consumer_secret = ''

with open('football_terms.txt') as f:
	vocab = [term.replace('\n', '') for term in f.readlines()]

with open('football_teams.txt') as f:
	for line in f:
		vocab.append(line.replace('\n', ''))

track_params = ','.join(vocab)

twitter_stream = TwitterStream(auth=OAuth(oauth_token, 
										  oauth_secret, 
										  consumer_key, 
										  consumer_secret))

iterator = twitter_stream.statuses.filter(track=track_params,language='en')

for tweet in iterator:
    if 'text' in tweet:
        print tweet
