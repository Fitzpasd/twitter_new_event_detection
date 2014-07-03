import numpy
import math
import itertools
from collections import defaultdict
from tweet import TweetVect
from scipy.spatial.distance import cosine

class BucketSet:
	def __init__(self, l, k, num_features, max_values):
		self.buckets = tuple(Bucket(k, num_features, max_values) for _ in xrange(l)) 
		self.max_comparisons = 3 * l

	def get_nearest_neighbour(self, tweetVect):
		set_of_collisions = itertools.chain(*[bucket.get_collisions_and_add_value(tweetVect)
											  for bucket in self.buckets])

		dist_and_tweetVecs = [(cosine(tweetVect.vect, collision.vect), collision) 
							  for collision in itertools.islice(set_of_collisions, 0, self.max_comparisons)]

		return min(dist_and_tweetVecs, key=lambda x: x[0]) if len(dist_and_tweetVecs) else None

class Bucket:
	def __init__(self, k, num_features, max_values):
		self.hash_table = defaultdict(list)
		self.randv = 1 * numpy.random.randn(k, num_features) + 0
		self.max_values = max_values

	def get_collisions_and_add_value(self, tweetVect):
		sig = get_signature(tweetVect.vect, self.randv)

		pointer = self.hash_table[sig]
		res = list(pointer)
		
		if len(res) >= self.max_values:
			pointer.pop(0)

		pointer.append(tweetVect)
		
		return res


def get_signature(user_vector, rand_projs): 
    res = 0
    for p in rand_projs:
        res = res << 1
        val = numpy.dot(p, user_vector)
        if val >= 0:
            res |= 1
    return res

def num_ones(num):
    if num == 0:
        return 0
    res = 1
    num = num & (num-1)
    while num:
        res += 1
        num = num & (num-1)
    return res

def hash_similarity(sig1, sig2, k):
	matching_bits = sig1 ^ sig2	
	num_matching_bits = num_ones(matching_bits)
	return (k - num_matching_bits)/float(k)

def cosine_sim(vect1, vect2):
	dot_prod = numpy.dot(vect1, vect2)
	sum_v1 = sum(vect1 ** 2) ** 0.5
	sum_v2 = sum(vect2 ** 2) ** 0.5
	cosine = dot_prod / (sum_v1 / sum_v2)
	theta = math.acos(cosine)
	return 1.0 - (theta / math.pi)
