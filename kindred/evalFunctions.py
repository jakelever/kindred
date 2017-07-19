
import kindred
from collections import Counter

def evaluate(goldCorpus,testCorpus,metric='f1score',display=True):
	""" Compares the gold corpus with the test corpus and calculate appropriate metrics.
	
	:params goldCorpus: The gold standard set of data
	:type name: str
	:params testCorpus: The test set for comparison
	:type state: bool
	:params metric: Which metric to use (precision/recall/f1score)
	:type name: str
	:returns: float -- the score given the metric
	"""

	assert isinstance(goldCorpus,kindred.Corpus)
	assert isinstance(testCorpus,kindred.Corpus)

	TPs,FPs,FNs = Counter(),Counter(),Counter()
	
	#goldTuples = [ ]
	#for doc in goldCorpus.documents:
	#	relTuples = [ (r.relationType,tuple(r.entityIDs)) for r in doc.getRelations() ]
	#	goldTuples += relTuples
		
	goldTuples = [ (r.relationType,tuple(r.entityIDs)) for r in goldCorpus.getRelations() ]
	testTuples = [ (r.relationType,tuple(r.entityIDs)) for r in testCorpus.getRelations() ]

	totalSet = set(goldTuples + testTuples)
	for relation in totalSet:
		inGold = relation in goldTuples
		inTest = relation in testTuples

		relType = relation[0]
		
		if inGold and inTest:
			TPs[relType] += 1
		elif inGold:
			FNs[relType] += 1
		elif inTest:
			FPs[relType] += 1

	sortedRelTypes = sorted( list(set( [relation[0] for relation in totalSet] )))

	maxLen = max( [len(relType) for relType in sortedRelTypes ] )
	formatString = '%-' + str(maxLen) + 's\tTP:%d FP:%d FN:%d\tP:%f R:%f F1:%f'

	for relType in sortedRelTypes:
		TP,FP,FN = TPs[relType],FPs[relType],FNs[relType]
		precision = 0.0 if (TP+FP) == 0 else TP / float(TP+FP)
		recall = 0.0 if (TP+FN) == 0 else TP / float(TP+FN)
		f1score = 0.0 if precision==0 or recall == 0 else 2 * (precision*recall) / (precision+recall)
	
		if display:
			print(formatString % (relType,TP,FP,FN,precision,recall,f1score))

	TP,FP,FN = sum(TPs.values()),sum(FPs.values()),sum(FNs.values())
	precision = 0.0 if (TP+FP) == 0 else TP / float(TP+FP)
	recall = 0.0 if (TP+FN) == 0 else TP / float(TP+FN)
	f1score = 0.0 if precision==0 or recall == 0 else 2 * (precision*recall) / (precision+recall)

	if display:
		print("-"*50)
		print(formatString % ("All",TP,FP,FN,precision,recall,f1score))


	
	if metric == 'f1score':
		return f1score
	elif metric == 'precision':
		return precision
	elif metric == 'recall':
		return recall
	elif metric == 'all':
		return precision,recall,f1score	
	else:
		raise RuntimeError('Unknown metric: %s' % metric)

