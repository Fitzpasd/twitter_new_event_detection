import re

non_word_characters = re.compile('\W+')
mentions = re.compile(' @\w+')

def remove_grammar(text):
	words = [non_word_characters.sub('', word) for word in text.split()]
	return ' '.join([w for w in words if w])

def remove_mentions(text):
	return mentions.sub('', text)
