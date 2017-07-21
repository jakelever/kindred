import numpy as np
import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer

from kindred.datageneration import generateData,generateTestData
	
def test_simpleVectorizer():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease> . <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text)
	
	candidateBuilder = CandidateBuilder()
	candidateBuilder.fit_transform(corpus)
	
	# We'll just get the vectors for the selectedTokenTypes
	vectorizer = Vectorizer()
	vectors = vectorizer.fit_transform(corpus)
	
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
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	candidateBuilder = CandidateBuilder()
	candidateBuilder.fit_transform(corpus1)
	candidateBuilder.transform(corpus2)

	candidates = corpus1.getCandidateRelations()

	chosenFeatures = ["selectedTokenTypes"]
	vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(corpus1)
	matrix2 = vectorizer.transform(corpus2)
		
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['selectedtokentypes_0_disease', 'selectedtokentypes_0_disease2', 'selectedtokentypes_0_drug', 'selectedtokentypes_1_disease', 'selectedtokentypes_1_disease2', 'selectedtokentypes_1_drug']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[ 2,2,4, 2,2,4 ]]
	
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[ 5,4,9, 5,4,9 ]]
	
def test_vectorizer_ngrams_betweenEntities():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	candidateBuilder = CandidateBuilder()
	candidateBuilder.fit_transform(corpus1)
	candidateBuilder.transform(corpus2)

	chosenFeatures = ["ngrams_betweenEntities"]
	vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(corpus1)
	matrix2 = vectorizer.transform(corpus2)
			
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'ngrams_betweenentities_a', u'ngrams_betweenentities_be', u'ngrams_betweenentities_can', u'ngrams_betweenentities_clinical', u'ngrams_betweenentities_common', u'ngrams_betweenentities_effect', u'ngrams_betweenentities_failed', u'ngrams_betweenentities_for', u'ngrams_betweenentities_is', u'ngrams_betweenentities_known', u'ngrams_betweenentities_of', u'ngrams_betweenentities_side', u'ngrams_betweenentities_treated', u'ngrams_betweenentities_treatment', u'ngrams_betweenentities_trials', u'ngrams_betweenentities_with']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [1.4519522547520485, 1.0, 1.0, 1.0581526716744893, 1.037330992404908, 0.8817459917627732, 1.0581526716744893, 1.5854195824122916, 1.4519522547520485, 0.8817459917627732, 0.8817459917627732, 0.8817459917627732, 1.0, 1.037330992404908, 1.0581526716744893, 1.0]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	expected2 = [1.4519522547520485, 1.0, 1.0, 1.0581526716744893, 1.037330992404908, 0.8817459917627732, 1.0581526716744893, 1.5854195824122916, 1.4519522547520485, 0.8817459917627732, 0.8817459917627732, 0.8817459917627732, 1.0, 1.037330992404908, 1.0581526716744893, 1.0]
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
	
def test_vectorizer_bigrams():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	candidateBuilder = CandidateBuilder()
	candidateBuilder.fit_transform(corpus1)
	candidateBuilder.transform(corpus2)

	chosenFeatures = ["bigrams"]
	vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(corpus1)
	matrix2 = vectorizer.transform(corpus2)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'bigrams_a_common', u'bigrams_a_known', u'bigrams_be_treated', u'bigrams_bmzvpvwbpw_failed', u'bigrams_can_be', u'bigrams_clinical_trials', u'bigrams_common_treatment', u'bigrams_effect_of', u'bigrams_failed_clinical', u'bigrams_for_kyekjnkrfo', u'bigrams_for_zgwivlcmly', u'bigrams_gnorcyvmer_is', u'bigrams_is_a', u'bigrams_known_side', u'bigrams_kyekjnkrfo_.', u'bigrams_of_ruswdgzajr', u'bigrams_ootopaoxbg_can', u'bigrams_pehhjnlvvewbjccovflf_is', u'bigrams_ruswdgzajr_.', u'bigrams_side_effect', u'bigrams_treated_with', u'bigrams_treatment_for', u'bigrams_trials_for', u'bigrams_vgypkemhjr_.', u'bigrams_with_vgypkemhjr', u'bigrams_zgwivlcmly_.']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [0.7801302536256829, 0.726795880099511, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 0.726795880099511, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 0.726795880099511, 1.1401235154492921, 0.726795880099511, 0.8164965809277259, 0.726795880099511, 0.8164965809277259, 0.7801302536256829, 0.726795880099511, 0.726795880099511, 0.8164965809277259, 0.7801302536256829, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	# As a quick check, we'll confirm that the column means are as expected
	expected2 = [1.0581526716744893, 0.0, 0.8164965809277259, 1.0, 0.8164965809277259, 2.1547005383792515, 1.0581526716744893, 0.0, 2.1547005383792515, 0.0, 0.0, 0.0, 0.8005865164268136, 0.0, 2.0, 0.0, 0.8164965809277259, 2.0, 0.0, 0.0, 0.8164965809277259, 1.0581526716744893, 2.1547005383792515, 0.8164965809277259, 0.8164965809277259, 0.0]
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	
def test_vectorizer_dependencyPathElements():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	candidateBuilder = CandidateBuilder()
	candidateBuilder.fit_transform(corpus1)
	candidateBuilder.transform(corpus2)

	chosenFeatures = ["dependencyPathElements"]
	vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(corpus1)
	matrix2 = vectorizer.transform(corpus2)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'dependencypathelements_nmod', u'dependencypathelements_nsubj', u'dependencypathelements_nsubjpass', u'dependencypathelements_punct']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[ 8, 6, 2, 4 ]]
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[ 10, 14, 2, 6 ]]
	
	
def test_vectorizer_dependencyPathNearSelected():
	corpus1, _ = generateTestData(positiveCount=5,negativeCount=5)
	corpus2, _ = generateTestData(positiveCount=10,negativeCount=10)

	candidateBuilder = CandidateBuilder()
	candidateBuilder.fit_transform(corpus1)
	candidateBuilder.transform(corpus2)

	chosenFeatures = ["dependencyPathNearSelected"]
	vectorizer = Vectorizer(featureChoice=chosenFeatures,tfidf=True)
	
	matrix1 = vectorizer.fit_transform(corpus1)
	matrix2 = vectorizer.transform(corpus2)
	
	colnames = vectorizer.getFeatureNames()
	print colnames
	expectedNames = ['dependencypathnearselectedtoken_0_nsubj', 'dependencypathnearselectedtoken_0_nsubjpass', 'dependencypathnearselectedtoken_1_nsubj', 'dependencypathnearselectedtoken_1_nsubjpass']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[ 3, 1, 3, 1 ]]
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[ 7, 1, 7, 1 ]]
	


if __name__ == '__main__':
	test_vectorizer_selectedTokenTypes()
