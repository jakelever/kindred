import numpy as np
import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer

from kindred.datageneration import generateData,generateTestData
	
def test_simpleVectorizer():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease> . <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text)
	
	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)
	
	# We'll just get the vectors for the selectedTokenTypes
	vectorizer = Vectorizer()
	vectors = vectorizer.transform(corpus,candidateRelations)
	
	tuples = [(0, 2),(1, 0),(2, 2),(3, 1),(0, 3),(1, 5),(2, 4),(3, 5)]
	expectedRows = [ r for r,c in tuples ]
	expectedCols = [ c for r,c in tuples ]
	
	rows,cols = vectors.nonzero()
	assert expectedRows == rows.tolist()
	assert expectedCols == cols.tolist()
	
	vectorsCSR = vectors.tocsr()
	for r,c in tuples:
		assert vectorsCSR[r,c] == 1.0

def test_vectorizer_selectedTokenTypes():
	corpus, _ = generateTestData(positiveCount=8,negativeCount=8)

	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)

	chosenFeatures = ["selectedTokenTypes"]
	vectorizer = Vectorizer()
	
	matrix = vectorizer.transform(corpus,candidateRelations,featureChoice=chosenFeatures,tfidf=True)
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans = np.sum(matrix,axis=0)
	assert colmeans.tolist() == [[ 5,2,7, 5,2,7 ]]
	
def test_vectorizer_ngrams_betweenEntities():
	corpus, _ = generateTestData(positiveCount=8,negativeCount=8)

	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)

	chosenFeatures = ["ngrams_betweenEntities"]
	vectorizer = Vectorizer()
	
	matrix = vectorizer.transform(corpus,candidateRelations,featureChoice=chosenFeatures,tfidf=True)
	
	# As a quick check, we'll confirm that the column means are as expected
	expected = [ 1.90474276 , 1. , 1. , 0.94744995 , 1.0758251 , 1.90474276 , 1.0758251 , 2.32585296 , 2.23916188 , 0.94744995 , 0.94744995 , 0.94744995 , 1. , 1.90474276 , 4. , 1.0758251 , 1. ]
	colmeans = np.sum(matrix,axis=0).tolist()[0]
	for gotVal,expectedVal in zip(colmeans,expected):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
	
def test_vectorizer_bigrams():
	corpus, _ = generateTestData(positiveCount=8,negativeCount=8)

	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)

	chosenFeatures = ["bigrams"]
	vectorizer = Vectorizer()
	
	matrix = vectorizer.transform(corpus,candidateRelations,featureChoice=chosenFeatures,tfidf=True)
	
	# As a quick check, we'll confirm that the column means are as expected
	expected = [ 1.3609683196826348, 0.816496580927726, 0.8461215895327386, 0.816496580927726, 0.77575336284949, 0.8416446466035913, 1.3609683196826348, 0.77575336284949, 0.8416446466035913, 0.8416446466035913, 0.8461215895327386, 0.8461215895327389, 1.1547005383792517, 1.1547005383792517, 1.3609683196826348, 0.77575336284949, 1.3007748995029198, 0.8461215895327386, 0.816496580927726, 0.77575336284949, 0.77575336284949, 0.8416446466035913, 0.8461215895327389, 0.816496580927726, 0.77575336284949, 0.816496580927726, 1.3609683196826348, 1.1547005383792517, 1.1547005383792517, 0.8416446466035913, 1.1547005383792517, 1.1547005383792517, 0.816496580927726, 0.8461215895327389 ]
	colmeans = np.sum(matrix,axis=0).tolist()[0]
	for gotVal,expectedVal in zip(colmeans,expected):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
	
def test_vectorizer_dependencyPathElements():
	corpus, _ = generateTestData(positiveCount=8,negativeCount=8)

	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)

	chosenFeatures = ["dependencyPathElements"]
	vectorizer = Vectorizer()
	
	matrix = vectorizer.transform(corpus,candidateRelations,featureChoice=chosenFeatures,tfidf=True)
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans = np.sum(matrix,axis=0)
	assert colmeans.tolist() == [[ 4, 10, 12, 2, 4 ]]
	
def test_vectorizer_dependencyPathNearSelected():
	corpus, _ = generateTestData(positiveCount=8,negativeCount=8)

	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(corpus)

	chosenFeatures = ["dependencyPathNearSelected"]
	vectorizer = Vectorizer()
	
	matrix = vectorizer.transform(corpus,candidateRelations,featureChoice=chosenFeatures,tfidf=True)
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans = np.sum(matrix,axis=0)
	assert colmeans.tolist() == [[ 6, 1, 6, 1 ]]
	


if __name__ == '__main__':
	test_vectorizer_selectedTokenTypes()
