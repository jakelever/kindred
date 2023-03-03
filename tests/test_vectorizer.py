import numpy as np
import kindred
import os
import json

from kindred.datageneration import generateData,generateTestData	

def test_simpleVectorizer_binary():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease> . <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	parser = kindred.Parser()
	parser.parse(corpus)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations = candidateBuilder.build(corpus)
	
	# We'll just get the vectors for the entityTypes
	vectorizer = kindred.Vectorizer(featureChoice=["entityTypes"])
	vectors = vectorizer.fit_transform(candidateRelations)

	assert vectors.shape[0] == 4
	assert len(vectors.nonzero()) > 0

def test_simpleVectorizer_triple():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer> which targets <gene id="3">EGFR</gene>. <relation type="druginfo" drug="1" disease="2" gene="3" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
		
	parser = kindred.Parser()
	parser.parse(corpus)
	
	candidateBuilder = kindred.CandidateBuilder(entityCount=3)
	candidateRelations = candidateBuilder.build(corpus)
	
	# We'll just get the vectors for the entityTypes
	vectorizer = kindred.Vectorizer(entityCount=3,featureChoice=["entityTypes"])
	vectors = vectorizer.fit_transform(candidateRelations)
	
	assert vectors.shape[0] == 6
	assert len(vectors.nonzero()) > 0

def test_vectorizer_defaults():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	vectorizer = kindred.Vectorizer()
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0

def test_vectorizer_entityTypes():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)
	
	chosenFeatures = ["entityTypes"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0
	
def test_vectorizer_unigramsBetweenEntities():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)
	
	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["unigramsBetweenEntities"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0
	
def test_vectorizer_bigrams():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["bigrams"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)

	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0
	
def test_vectorizer_dependencyPathEdges():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["dependencyPathEdges"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)

	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0
	
def test_vectorizer_dependencyPathEdgesNearEntities():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["dependencyPathEdgesNearEntities"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0

def test_vectorizer_entityTypes_noTFIDF():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)
	
	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["entityTypes"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=False)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0
	
def test_vectorizer_unigramsBetweenEntities_noTFIDF():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["unigramsBetweenEntities"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=False)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0
	
def test_vectorizer_bigrams_noTFIDF():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)
	
	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["bigrams"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=False)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0

def test_vectorizer_dependencyPathEdges_noTFIDF():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["dependencyPathEdges"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=False)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0

def test_vectorizer_dependencyPathEdgesNearEntities_noTFIDF():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	chosenFeatures = ["dependencyPathEdgesNearEntities"]
	vectorizer = kindred.Vectorizer(featureChoice=chosenFeatures,tfidf=False)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)
	
	assert matrix1.shape[0] == 8
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 18
	assert len(matrix2.nonzero()) > 0

def test_vectorizer_defaults_triple():
	corpus1, _ = generateTestData(entityCount=3,positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(entityCount=3,positiveCount=10,negativeCount=10)

	parser = kindred.Parser()
	parser.parse(corpus1)
	parser.parse(corpus2)
	
	candidateBuilder = kindred.CandidateBuilder(entityCount=3)
	candidateRelations1 = candidateBuilder.build(corpus1)
	candidateRelations2 = candidateBuilder.build(corpus2)

	vectorizer = kindred.Vectorizer(entityCount=3)
	
	matrix1 = vectorizer.fit_transform(candidateRelations1)
	matrix2 = vectorizer.transform(candidateRelations2)

	assert matrix1.shape[0] == 18
	assert len(matrix1.nonzero()) > 0
	assert matrix2.shape[0] == 60
	assert len(matrix2.nonzero()) > 0

if __name__ == '__main__':
	test_vectorizer_defaults_triple()

