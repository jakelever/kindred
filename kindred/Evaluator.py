
class Evaluator():
	""" A test doc string for the RelationsEvaluator"""

	def __init__(self):
		pass

	def evaluate(self,goldSet,testSet,metric='f1score'):
		""" This does something
		
		:params goldSet: The gold standard set of data
		:type name: str
		:params testSet: The test set for comparison
		:type state: bool
		:params metric: Which metric to use (precision/recall/f1score)
		:type name: str
		:returns: float -- the score given the metric
		"""

		TP,FP,FN = 0,0,0
		
		goldTuples = [ ]
		for relations in goldSet:
			relTuples = [ (r.relationType,tuple(r.entityIDs)) for r in relations ]
			goldTuples += relTuples
			
		testTuples = [ (r.relationType,tuple(r.entityIDs)) for r in testSet ]

		totalSet = set(goldTuples + testTuples)
		for relation in totalSet:
			inGold = relation in goldTuples
			inTest = relation in testTuples
			
			if inGold and inTest:
				TP += 1
			elif inGold:
				FN += 1
			elif inTest:
				FP += 1

		print "TP:%d FP:%d FN:%d" % (TP,FP,FN)		
		precision = TP / float(TP+FP)
		recall = TP / float(TP+FN)
		f1score = 2 * (precision*recall) / (precision+recall)

		
		if metric == 'f1score':
			return f1score
		elif metric == 'precision':
			return precision
		elif metric == 'recall':
			return recall
		else:
			raise RuntimeError('Unknown metric: %s' % metric)

