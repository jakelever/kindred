import kindred
from collections import Counter

def test_corpus_split():
	mainCorpus = kindred.Corpus()
	for i in range(100):
		doc = kindred.Document(text=str(i),entities=[])
		mainCorpus.addDocument(doc)
	
	corpusA,corpusB = mainCorpus.split(0.75)

	assert len(corpusA.documents) == 75
	assert len(corpusB.documents) == 25

	seen = set()
	for doc in corpusA.documents:
		assert doc in mainCorpus.documents, "This document doesn't match an existing one"
		assert not doc in seen, "This document isn't unique now"
		seen.add(doc)
	for doc in corpusB.documents:
		assert doc in mainCorpus.documents, "This document doesn't match an existing one"
		assert not doc in seen, "This document isn't unique now"
		seen.add(doc)

	assert len(seen) == len(mainCorpus.documents)

def test_corpus_nfold_split():
	mainCorpus = kindred.Corpus()
	docCount = 100
	for i in range(docCount):
		doc = kindred.Document(text=str(i),entities=[])
		mainCorpus.addDocument(doc)
	
	corpusA,corpusB = mainCorpus.split(0.75)
	folds = 5
	trainCounter,testCounter = Counter(),Counter()
	for trainCorpus,testCorpus in mainCorpus.nfold_split(folds):
		assert len(trainCorpus.documents) == (folds-1) * docCount / folds
		assert len(testCorpus.documents) == docCount / folds
		
		seen = set()
		for doc in corpusA.documents:
			assert doc in mainCorpus.documents, "This document doesn't match an existing one"
			assert not doc in seen, "This document isn't unique now"
			trainCounter[doc] += 1
		for doc in corpusB.documents:
			assert doc in mainCorpus.documents, "This document doesn't match an existing one"
			assert not doc in seen, "This document isn't unique now"
			testCounter[doc] += 1

	for doc,count in trainCounter.items():
		assert count == folds
	for doc,count in testCounter.items():
		assert count == folds

