from collections import defaultdict
import threading

GOAL_TERMS = ['score', 'goal', 'goals', 'scores', 'scored']
OFFSIDE_TERMS = ['offside', 'off side']
HALFTIME_TERMS = ['half time', 'halftime']
PENALTY_TERMS = ['penalty']
FULLTIME_TERMS = ['full time', 'fulltime']
YELLOWCARD_TERMS = ['yellow card', 'yellow for']
REDCARD_TERMS = ['red card', 'sent off', 'red for']
SUB_TERMS = ['sub', 'change for', 'replaced by']
CORNER_TERMS = ['corner']
FREEKICK_TERMS = ['freekick', 'free kick']
HANDBALL_TERMS = ['handball', 'hand ball']

GOAL = 1
OFFSIDE = 2
YELLOW = 3
PENALTY = 4
SUB = 5
HALFTIME = 6
FULLTIME = 7
RED = 8
CORNER = 9
FREEKICK = 10
HANDBALL = 11

STR_MAP = {1:'Goal', 2:'Offside', 3:'Yellow', 
		   4:'Penalty', 5:'Sub', 6:'Halftime', 
		   7:'Fulltime', 8:'Red', 9:'Corner', 
		   10:'Freekick', 11:'Handball'}

class FootballRecognizer(threading.Thread):
	def __init__(self):
		super(FootballRecognizer, self).__init__()
		self.thread_queue = []
		self.events = []
		self.running = True
		self.cv = threading.Condition()

	def run(self):
		while self.running:
			self.cv.acquire()
			while not self.thread_queue:
				self.cv.wait()

			for thread in self.thread_queue:
				texts = thread.get_texts()
				event = classify_list(texts)

				if event:
					print '%s|%s' % (STR_MAP[event], thread.get_timestr())

				self.thread_queue.remove(thread)
			self.cv.release()

	def recognize_thread(self, thread):
		self.cv.acquire()
		self.thread_queue.append(thread)
		self.cv.notify()
		self.cv.release()

	def stop(self):
		self.running = False
			
def classify_list(texts):
	votes = defaultdict(int)

	for text in texts:
		lower_text = text.lower()

		if any([term in text for term in GOAL_TERMS]):
			votes[GOAL] += 1

		if any([term in text for term in OFFSIDE_TERMS]):
			votes[OFFSIDE] += 1

		if any([term in text for term in YELLOWCARD_TERMS]):
			votes[YELLOW] += 1

		if any([term in text for term in PENALTY_TERMS]):
			votes[PENALTY] += 1

		if any([term in text for term in SUB_TERMS]):
			votes[SUB] += 1

		if any([term in text for term in HALFTIME_TERMS]):
			votes[HALFTIME] += 1

		if any([term in text for term in FULLTIME_TERMS]):
			votes[FULLTIME] += 1

		if any([term in text for term in REDCARD_TERMS]):
			votes[RED] += 1

		if any([term in text for term in CORNER_TERMS]):
			votes[CORNER] += 1

		if any([term in text for term in FREEKICK_TERMS]):
			votes[FREEKICK] += 1

		if any([term in text for term in HANDBALL_TERMS]):
			votes[HANDBALL] += 1

	if len(votes):
		winner = max(votes.iteritems(), key=lambda (k,v):v)
		if winner[1] > len(texts)/2:
			return winner[0]
