import numpy as np
import kindred

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

	assert vectors.shape == (4,6)
	
	expected = [(0, 2),(1, 0),(2, 2),(3, 1),(0, 3),(1, 5),(2, 4),(3, 5)]
	
	rows,cols = vectors.nonzero()
	rowsWithCols = list(zip(rows.tolist(),cols.tolist()))
	assert sorted(expected) == sorted(rowsWithCols)
	
	vectorsCSR = vectors.tocsr()
	for r,c in expected:
		assert vectorsCSR[r,c] == 1.0

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

	assert vectors.shape == (6,9)
	
	expected = [(0, 1), (0, 3), (0, 8), (1, 1), (1, 5), (1, 6), (2, 0), (2, 4), (2, 8), (3, 0), (3, 5), (3, 7), (4, 2), (4, 4), (4, 6), (5, 2), (5, 3), (5, 7)]
	
	rows,cols = vectors.nonzero()
	rowsWithCols = list(zip(rows.tolist(),cols.tolist()))
	assert sorted(expected) == sorted(rowsWithCols)
	
	vectorsCSR = vectors.tocsr()
	for r,c in expected:
		assert vectorsCSR[r,c] == 1.0

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

	assert matrix1.shape == (8,60)
	assert matrix2.shape == (18,60)

	colnames = vectorizer.getFeatureNames()
	expectedNames = ['selectedtokentypes_0_disease', 'selectedtokentypes_0_disease2', 'selectedtokentypes_0_drug', 'selectedtokentypes_1_disease', 'selectedtokentypes_1_disease2', 'selectedtokentypes_1_drug', 'ngrams_betweenentities_a', 'ngrams_betweenentities_be', 'ngrams_betweenentities_can', 'ngrams_betweenentities_clinical', 'ngrams_betweenentities_common', 'ngrams_betweenentities_effect', 'ngrams_betweenentities_failed', 'ngrams_betweenentities_for', 'ngrams_betweenentities_is', 'ngrams_betweenentities_known', 'ngrams_betweenentities_of', 'ngrams_betweenentities_side', 'ngrams_betweenentities_treated', 'ngrams_betweenentities_treatment', 'ngrams_betweenentities_trials', 'ngrams_betweenentities_with', 'bigrams_ _gnorcyvmer', 'bigrams_a_common', 'bigrams_a_known', 'bigrams_be_treated', 'bigrams_bmzvpvwbpw_failed', 'bigrams_can_be', 'bigrams_clinical_trials', 'bigrams_common_treatment', 'bigrams_effect_of', 'bigrams_failed_clinical', 'bigrams_for_kyekjnkrfo', 'bigrams_for_zgwivlcmly', 'bigrams_gnorcyvmer_is', 'bigrams_is_a', 'bigrams_known_side', 'bigrams_kyekjnkrfo_.', 'bigrams_of_ruswdgzajr', 'bigrams_ootopaoxbg_can', 'bigrams_pehhjnlvvewbjccovflf_is', 'bigrams_ruswdgzajr_.', 'bigrams_side_effect', 'bigrams_treated_with', 'bigrams_treatment_for', 'bigrams_trials_for', 'bigrams_vgypkemhjr_.', 'bigrams_with_vgypkemhjr', 'bigrams_zgwivlcmly_.', 'dependencypathelements_attr', 'dependencypathelements_nsubj', 'dependencypathelements_nsubjpass', 'dependencypathelements_pobj', 'dependencypathelements_prep', 'dependencypathnearselectedtoken_0_nsubj', 'dependencypathnearselectedtoken_0_nsubjpass', 'dependencypathnearselectedtoken_0_pobj', 'dependencypathnearselectedtoken_1_nsubj', 'dependencypathnearselectedtoken_1_nsubjpass', 'dependencypathnearselectedtoken_1_pobj']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [2.0, 2.0, 4.0, 2.0, 2.0, 4.0, 1.4519522547520485, 1.0, 1.0, 1.0581526716744893, 1.037330992404908, 0.8817459917627732, 1.0581526716744893, 1.5854195824122916, 1.4519522547520485, 0.8817459917627732, 0.8817459917627732, 0.8817459917627732, 1.0, 1.037330992404908, 1.0581526716744893, 1.0, 0.6830902801437798, 0.7801302536256829, 0.6830902801437798, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 0.6830902801437798, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 0.6830902801437798, 1.1070563456981333, 0.6830902801437798, 0.8164965809277259, 0.6830902801437798, 0.8164965809277259, 0.7801302536256829, 0.6830902801437798, 0.6830902801437798, 0.8164965809277259, 0.7801302536256829, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 4.0, 4.0, 2.0, 10.0, 8.0, 2.0, 1.0, 1.0, 2.0, 1.0, 1.0]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected1) == len(colmeans1)
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	# As a quick check, we'll confirm that the column means are as expected
	expected2 = [5.0, 4.0, 9.0, 5.0, 4.0, 9.0, 0.7848330659854781, 1.0, 1.0, 2.1163053433489787, 1.037330992404908, 0.0, 2.1163053433489787, 2.386006098839105, 1.99154811934689, 0.0, 1.594941622753311, 0.0, 1.0, 1.037330992404908, 2.1163053433489787, 1.0, 0.0, 1.0581526716744893, 0.0, 0.8164965809277259, 1.0, 0.8164965809277259, 2.1547005383792515, 1.0581526716744893, 0.0, 2.1547005383792515, 0.0, 0.0, 0.0, 0.8005865164268136, 0.0, 2.0, 0.0, 0.8164965809277259, 2.0, 0.0, 0.0, 0.8164965809277259, 1.0581526716744893, 2.1547005383792515, 0.8164965809277259, 0.8164965809277259, 0.0, 4.0, 10.0, 2.0, 10.0, 10.0, 3.0, 1.0, 0.0, 3.0, 1.0, 0.0]
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	assert len(expected2) == len(colmeans2)
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)

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
	
	assert matrix1.shape == (8,6)
	assert matrix2.shape == (18,6)
		
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['selectedtokentypes_0_disease', 'selectedtokentypes_0_disease2', 'selectedtokentypes_0_drug', 'selectedtokentypes_1_disease', 'selectedtokentypes_1_disease2', 'selectedtokentypes_1_drug']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[ 2,2,4, 2,2,4 ]]
	
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[ 5,4,9, 5,4,9 ]]
	
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
	
	assert matrix1.shape == (8,16)
	assert matrix2.shape == (18,16)
			
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'ngrams_betweenentities_a', u'ngrams_betweenentities_be', u'ngrams_betweenentities_can', u'ngrams_betweenentities_clinical', u'ngrams_betweenentities_common', u'ngrams_betweenentities_effect', u'ngrams_betweenentities_failed', u'ngrams_betweenentities_for', u'ngrams_betweenentities_is', u'ngrams_betweenentities_known', u'ngrams_betweenentities_of', u'ngrams_betweenentities_side', u'ngrams_betweenentities_treated', u'ngrams_betweenentities_treatment', u'ngrams_betweenentities_trials', u'ngrams_betweenentities_with']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [1.4519522547520485, 1.0, 1.0, 1.0581526716744893, 1.037330992404908, 0.8817459917627732, 1.0581526716744893, 1.5854195824122916, 1.4519522547520485, 0.8817459917627732, 0.8817459917627732, 0.8817459917627732, 1.0, 1.037330992404908, 1.0581526716744893, 1.0]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected1) == len(colmeans1)
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	expected2 = [1.4519522547520485, 1.0, 1.0, 1.0581526716744893, 1.037330992404908, 0.8817459917627732, 1.0581526716744893, 1.5854195824122916, 1.4519522547520485, 0.8817459917627732, 0.8817459917627732, 0.8817459917627732, 1.0, 1.037330992404908, 1.0581526716744893, 1.0]
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected2) == len(colmeans2)
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
	
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

	assert matrix1.shape == (8,27)
	assert matrix2.shape == (18,27)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'bigrams_ _gnorcyvmer', u'bigrams_a_common', u'bigrams_a_known', u'bigrams_be_treated', u'bigrams_bmzvpvwbpw_failed', u'bigrams_can_be', u'bigrams_clinical_trials', u'bigrams_common_treatment', u'bigrams_effect_of', u'bigrams_failed_clinical', u'bigrams_for_kyekjnkrfo', u'bigrams_for_zgwivlcmly', u'bigrams_gnorcyvmer_is', u'bigrams_is_a', u'bigrams_known_side', u'bigrams_kyekjnkrfo_.', u'bigrams_of_ruswdgzajr', u'bigrams_ootopaoxbg_can', u'bigrams_pehhjnlvvewbjccovflf_is', u'bigrams_ruswdgzajr_.', u'bigrams_side_effect', u'bigrams_treated_with', u'bigrams_treatment_for', u'bigrams_trials_for', u'bigrams_vgypkemhjr_.', u'bigrams_with_vgypkemhjr', u'bigrams_zgwivlcmly_.']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [0.6830902801437798, 0.7801302536256829, 0.6830902801437798, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 0.6830902801437798, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829, 0.6830902801437798, 1.1070563456981333, 0.6830902801437798, 0.8164965809277259, 0.6830902801437798, 0.8164965809277259, 0.7801302536256829, 0.6830902801437798, 0.6830902801437798, 0.8164965809277259, 0.7801302536256829, 0.8164965809277259, 0.8164965809277259, 0.8164965809277259, 0.7801302536256829]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected1) == len(colmeans1)
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	# As a quick check, we'll confirm that the column means are as expected
	expected2 = [0.0, 1.0581526716744893, 0.0, 0.8164965809277259, 1.0, 0.8164965809277259, 2.1547005383792515, 1.0581526716744893, 0.0, 2.1547005383792515, 0.0, 0.0, 0.0, 0.8005865164268136, 0.0, 2.0, 0.0, 0.8164965809277259, 2.0, 0.0, 0.0, 0.8164965809277259, 1.0581526716744893, 2.1547005383792515, 0.8164965809277259, 0.8164965809277259, 0.0]
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	assert len(expected2) == len(colmeans2)
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
	
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

	assert matrix1.shape == (8,5)
	assert matrix2.shape == (18,5)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['dependencypathelements_attr', 'dependencypathelements_nsubj', 'dependencypathelements_nsubjpass', 'dependencypathelements_pobj', 'dependencypathelements_prep']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[4.0, 4.0, 2.0, 10.0, 8.0]]
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[4.0, 10.0, 2.0, 10.0, 10.0]]
	
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
	
	assert matrix1.shape == (8,6)
	assert matrix2.shape == (18,6)

	colnames = vectorizer.getFeatureNames()
	expectedNames = ['dependencypathnearselectedtoken_0_nsubj', 'dependencypathnearselectedtoken_0_nsubjpass', 'dependencypathnearselectedtoken_0_pobj', 'dependencypathnearselectedtoken_1_nsubj', 'dependencypathnearselectedtoken_1_nsubjpass', 'dependencypathnearselectedtoken_1_pobj']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[2.0, 1.0, 1.0, 2.0, 1.0, 1.0]]
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans2 = np.sum(matrix2,axis=0)

	assert colmeans2.tolist() == [[3.0, 1.0, 0.0, 3.0, 1.0, 0.0]]

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
	
	assert matrix1.shape == (8,6)
	assert matrix2.shape == (18,6)
		
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['selectedtokentypes_0_disease', 'selectedtokentypes_0_disease2', 'selectedtokentypes_0_drug', 'selectedtokentypes_1_disease', 'selectedtokentypes_1_disease2', 'selectedtokentypes_1_drug']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[ 2,2,4, 2,2,4 ]]
	
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[ 5,4,9, 5,4,9 ]]
	
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
	
	assert matrix1.shape == (8,16)
	assert matrix2.shape == (18,16)
			
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'ngrams_betweenentities_a', u'ngrams_betweenentities_be', u'ngrams_betweenentities_can', u'ngrams_betweenentities_clinical', u'ngrams_betweenentities_common', u'ngrams_betweenentities_effect', u'ngrams_betweenentities_failed', u'ngrams_betweenentities_for', u'ngrams_betweenentities_is', u'ngrams_betweenentities_known', u'ngrams_betweenentities_of', u'ngrams_betweenentities_side', u'ngrams_betweenentities_treated', u'ngrams_betweenentities_treatment', u'ngrams_betweenentities_trials', u'ngrams_betweenentities_with']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [4.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 4.0, 4.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected1) == len(colmeans1)
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	expected2 = [4.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 4.0, 4.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected2) == len(colmeans2)
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
	
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
	
	assert matrix1.shape == (8,27)
	assert matrix2.shape == (18,27)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = [u'bigrams_ _gnorcyvmer', u'bigrams_a_common', u'bigrams_a_known', u'bigrams_be_treated', u'bigrams_bmzvpvwbpw_failed', u'bigrams_can_be', u'bigrams_clinical_trials', u'bigrams_common_treatment', u'bigrams_effect_of', u'bigrams_failed_clinical', u'bigrams_for_kyekjnkrfo', u'bigrams_for_zgwivlcmly', u'bigrams_gnorcyvmer_is', u'bigrams_is_a', u'bigrams_known_side', u'bigrams_kyekjnkrfo_.', u'bigrams_of_ruswdgzajr', u'bigrams_ootopaoxbg_can', u'bigrams_pehhjnlvvewbjccovflf_is', u'bigrams_ruswdgzajr_.', u'bigrams_side_effect', u'bigrams_treated_with', u'bigrams_treatment_for', u'bigrams_trials_for', u'bigrams_vgypkemhjr_.', u'bigrams_with_vgypkemhjr', u'bigrams_zgwivlcmly_.']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected1) == len(colmeans1)
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	# As a quick check, we'll confirm that the column means are as expected
	expected2 = [0.0, 4.0, 0.0, 4.0, 4.0, 4.0, 8.0, 4.0, 0.0, 8.0, 0.0, 0.0, 0.0, 4.0, 0.0, 4.0, 0.0, 4.0, 4.0, 0.0, 0.0, 4.0, 4.0, 8.0, 4.0, 4.0, 0.0]
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	assert len(expected2) == len(colmeans2)
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)

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
	
	assert matrix1.shape == (8,5)
	assert matrix2.shape == (18,5)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['dependencypathelements_attr', 'dependencypathelements_nsubj', 'dependencypathelements_nsubjpass', 'dependencypathelements_pobj', 'dependencypathelements_prep']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[4.0, 4.0, 2.0, 10.0, 8.0]]
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[4.0, 10.0, 2.0, 10.0, 10.0]]

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
	
	assert matrix1.shape == (8,6)
	assert matrix2.shape == (18,6)
	
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['dependencypathnearselectedtoken_0_nsubj', 'dependencypathnearselectedtoken_0_nsubjpass', 'dependencypathnearselectedtoken_0_pobj', 'dependencypathnearselectedtoken_1_nsubj', 'dependencypathnearselectedtoken_1_nsubjpass', 'dependencypathnearselectedtoken_1_pobj']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0)
	assert colmeans1.tolist() == [[2., 1., 1., 2., 1., 1.]]
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans2 = np.sum(matrix2,axis=0)
	assert colmeans2.tolist() == [[3., 1., 0., 3., 1., 0.]]

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

	assert matrix1.shape == (18,101)
	assert matrix2.shape == (60,101)
		
	colnames = vectorizer.getFeatureNames()
	expectedNames = ['selectedtokentypes_0_disease', 'selectedtokentypes_0_drug', 'selectedtokentypes_0_gene', 'selectedtokentypes_1_disease', 'selectedtokentypes_1_drug', 'selectedtokentypes_1_gene', 'selectedtokentypes_2_disease', 'selectedtokentypes_2_drug', 'selectedtokentypes_2_gene', 'ngrams_betweenentities_0_1_and', 'ngrams_betweenentities_0_1_be', 'ngrams_betweenentities_0_1_by', 'ngrams_betweenentities_0_1_can', 'ngrams_betweenentities_0_1_fvdxdietdx', 'ngrams_betweenentities_0_1_inhibition', 'ngrams_betweenentities_0_1_knetvjnjun', 'ngrams_betweenentities_0_1_targets', 'ngrams_betweenentities_0_1_treated', 'ngrams_betweenentities_0_1_treats', 'ngrams_betweenentities_0_1_using', 'ngrams_betweenentities_0_1_zkrkzlyfef', 'ngrams_betweenentities_0_2_and', 'ngrams_betweenentities_0_2_be', 'ngrams_betweenentities_0_2_by', 'ngrams_betweenentities_0_2_can', 'ngrams_betweenentities_0_2_fvdxdietdx', 'ngrams_betweenentities_0_2_inhibition', 'ngrams_betweenentities_0_2_knetvjnjun', 'ngrams_betweenentities_0_2_targets', 'ngrams_betweenentities_0_2_treated', 'ngrams_betweenentities_0_2_treats', 'ngrams_betweenentities_0_2_using', 'ngrams_betweenentities_0_2_zkrkzlyfef', 'ngrams_betweenentities_1_2_and', 'ngrams_betweenentities_1_2_be', 'ngrams_betweenentities_1_2_by', 'ngrams_betweenentities_1_2_can', 'ngrams_betweenentities_1_2_fvdxdietdx', 'ngrams_betweenentities_1_2_inhibition', 'ngrams_betweenentities_1_2_knetvjnjun', 'ngrams_betweenentities_1_2_targets', 'ngrams_betweenentities_1_2_treated', 'ngrams_betweenentities_1_2_treats', 'ngrams_betweenentities_1_2_using', 'ngrams_betweenentities_1_2_zkrkzlyfef', 'bigrams_and_targets', 'bigrams_be_treated', 'bigrams_by_fvdxdietdx', 'bigrams_by_zkrkzlyfef', 'bigrams_can_be', 'bigrams_elvptnpvyc_.', 'bigrams_fvdxdietdx_inhibition', 'bigrams_hxlfssirgk_.', 'bigrams_inhibition_using', 'bigrams_knetvjnjun_and', 'bigrams_kyekjnkrfo_can', 'bigrams_oxzbaapqct_treats', 'bigrams_targets_hxlfssirgk', 'bigrams_treated_by', 'bigrams_treats_knetvjnjun', 'bigrams_usckfljzxu_.', 'bigrams_using_elvptnpvyc', 'bigrams_using_usckfljzxu', 'bigrams_zgwivlcmly_can', 'bigrams_zkrkzlyfef_inhibition', 'dependencypathelements_0_1_acl', 'dependencypathelements_0_1_advmod', 'dependencypathelements_0_1_agent', 'dependencypathelements_0_1_compound', 'dependencypathelements_0_1_conj', 'dependencypathelements_0_1_dobj', 'dependencypathelements_0_1_nsubjpass', 'dependencypathelements_0_1_pobj', 'dependencypathelements_0_2_acl', 'dependencypathelements_0_2_advmod', 'dependencypathelements_0_2_agent', 'dependencypathelements_0_2_compound', 'dependencypathelements_0_2_conj', 'dependencypathelements_0_2_dobj', 'dependencypathelements_0_2_nsubjpass', 'dependencypathelements_0_2_pobj', 'dependencypathelements_1_2_acl', 'dependencypathelements_1_2_advmod', 'dependencypathelements_1_2_agent', 'dependencypathelements_1_2_compound', 'dependencypathelements_1_2_conj', 'dependencypathelements_1_2_dobj', 'dependencypathelements_1_2_nsubjpass', 'dependencypathelements_1_2_pobj', 'dependencypathnearselectedtoken_0_compound', 'dependencypathnearselectedtoken_0_conj', 'dependencypathnearselectedtoken_0_dobj', 'dependencypathnearselectedtoken_0_nsubjpass', 'dependencypathnearselectedtoken_1_compound', 'dependencypathnearselectedtoken_1_conj', 'dependencypathnearselectedtoken_1_dobj', 'dependencypathnearselectedtoken_1_nsubjpass', 'dependencypathnearselectedtoken_2_compound', 'dependencypathnearselectedtoken_2_conj', 'dependencypathnearselectedtoken_2_dobj', 'dependencypathnearselectedtoken_2_nsubjpass']
	assert colnames == expectedNames
	
	# As a quick check, we'll confirm that the column means are as expected
	expected1 = [6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 1.4620174403662662, 2.089911361057128, 2.089911361057128, 2.089911361057128, 0.8510011029330441, 2.089911361057128, 0.8909306965737043, 1.4620174403662662, 2.089911361057128, 1.4620174403662662, 2.089911361057128, 0.8510011029330441, 1.4620174403662662, 2.089911361057128, 2.089911361057128, 2.089911361057128, 0.8510011029330442, 2.089911361057128, 0.8909306965737043, 1.4620174403662662, 2.089911361057128, 1.4620174403662662, 2.089911361057128, 0.8510011029330441, 1.4620174403662662, 2.089911361057128, 2.089911361057128, 2.089911361057128, 0.8510011029330442, 2.089911361057128, 0.8909306965737043, 1.4620174403662662, 2.089911361057128, 1.4620174403662662, 2.089911361057128, 0.8510011029330441, 2.4494897427831783, 3.151972689633972, 2.283202494909358, 2.283202494909358, 3.151972689633972, 2.283202494909358, 2.283202494909358, 2.4494897427831783, 3.151972689633972, 2.4494897427831783, 2.283202494909358, 2.4494897427831783, 2.4494897427831783, 3.151972689633972, 2.4494897427831783, 2.283202494909358, 2.283202494909358, 2.283202494909358, 2.283202494909358, 2.283202494909358, 8.0, 4.0, 8.0, 8.0, 4.0, 12.0, 8.0, 8.0, 8.0, 4.0, 8.0, 8.0, 4.0, 12.0, 8.0, 8.0, 8.0, 4.0, 8.0, 8.0, 4.0, 12.0, 8.0, 8.0, 4.0, 2.0, 2.0, 4.0, 4.0, 2.0, 2.0, 4.0, 4.0, 2.0, 2.0, 4.0]
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	assert len(expected1) == len(colmeans1)
	for gotVal,expectedVal in zip(colmeans1,expected1):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)
		
	# As a quick check, we'll confirm that the column means are as expected
	expected2 = [8.0, 20.0, 20.0, 8.0, 20.0, 20.0, 8.0, 20.0, 20.0, 5.237574707711817, 0.0, 0.0, 0.0, 3.9169357592886755, 0.0, 0.8909306965737043, 18.69384731218667, 0.0, 3.095010602221718, 0.0, 0.0, 5.237574707711817, 0.0, 0.0, 0.0, 3.9169357592886755, 0.0, 0.8909306965737043, 18.69384731218667, 0.0, 3.095010602221718, 0.0, 0.0, 5.237574707711817, 0.0, 0.0, 0.0, 3.9169357592886755, 0.0, 0.8909306965737043, 18.69384731218667, 0.0, 3.095010602221718, 0.0, 0.0, 8.449489742783179, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.4494897427831783, 0.0, 2.4494897427831783, 0.0, 2.4494897427831783, 2.4494897427831783, 0.0, 2.4494897427831783, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 0.0, 12.0, 20.0, 28.0, 8.0, 28.0, 0.0, 4.0, 0.0, 12.0, 20.0, 28.0, 8.0, 28.0, 0.0, 4.0, 0.0, 12.0, 20.0, 28.0, 8.0, 28.0, 4.0, 10.0, 2.0, 4.0, 4.0, 10.0, 2.0, 4.0, 4.0, 10.0, 2.0, 4.0]
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	assert len(expected2) == len(colmeans2)
	for gotVal,expectedVal in zip(colmeans2,expected2):
		assert round(gotVal,8) == round(expectedVal,8) # Check rounded values (for floating point comparison issue)

if __name__ == '__main__':
	test_vectorizer_defaults_triple()

