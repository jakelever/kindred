import numpy as np
import kindred
import os
import json

from kindred.datageneration import generateData,generateTestData

def check(valueName,value):
	write = False

	scriptDir = os.path.dirname(__file__)
	jsonPath = os.path.join(scriptDir,'data','vectorizer','expected.json')
	if os.path.isfile(jsonPath):
		with open(jsonPath) as f:
			data = json.load(f)
	else:
		data = {}
	
	if write:
		data[valueName] = value
		with open(jsonPath,'w') as f:
			json.dump(data,f,indent=2,sort_keys=True)

	assert valueName in data
	assert data[valueName] == value
		

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
	vectorsCSR = vectors.tocsr()
	rows,cols = vectors.nonzero()

	expected = {(0, 2): 1.0, (0, 3): 1.0, (1, 0): 1.0, (1, 5): 1.0, (2, 2): 1.0, (2, 4): 1.0, (3, 1): 1.0, (3, 5): 1.0}

	namedCols = { str((r,c)):vectorsCSR[r,c] for r,c in zip(rows.tolist(),cols.tolist()) }

	check('test_simpleVectorizer_binary',namedCols)

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
	vectorsCSR = vectors.tocsr()
	rows,cols = vectors.nonzero()

	expected = {(0, 1): 1.0, (0, 3): 1.0, (0, 8): 1.0, (1, 1): 1.0, (1, 5): 1.0, (1, 6): 1.0, (2, 0): 1.0, (2, 4): 1.0, (2, 8): 1.0, (3, 0): 1.0, (3, 5): 1.0, (3, 7): 1.0, (4, 2): 1.0, (4, 4): 1.0, (4, 6): 1.0, (5, 2): 1.0, (5, 3): 1.0, (5, 7): 1.0}

	namedCols = { str((r,c)):vectorsCSR[r,c] for r,c in zip(rows.tolist(),cols.tolist()) }

	check('test_simpleVectorizer_triple',namedCols)

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

	colnames = vectorizer.getFeatureNames()
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_defaults_1',namedCols1)
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_defaults_2',namedCols2)

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
	
	colnames = vectorizer.getFeatureNames()
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_entityTypes_1',namedCols1)
	colmeans2 = np.sum(matrix2,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_entityTypes_2',namedCols2)
	
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
	
	colnames = vectorizer.getFeatureNames()
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_unigramsBetweenEntities_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_unigramsBetweenEntities_2',namedCols2)
	
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

	colnames = vectorizer.getFeatureNames()
	
	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_bigrams_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_bigrams_2',namedCols2)
	
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

	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_dependencyPathEdges_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_dependencyPathEdges_2',namedCols2)
	
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
	
	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_dependencyPathEdgesNearEntities_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_dependencyPathEdgesNearEntities_2',namedCols2)

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
	
	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_entityTypes_noTFIDF_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_entityTypes_noTFIDF_2',namedCols2)
	
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
	
	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_unigramsBetweenEntities_noTFIDF_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_unigramsBetweenEntities_noTFIDF_2',namedCols2)
	
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
	
	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_bigrams_noTFIDF_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_bigrams_noTFIDF_2',namedCols2)

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
	
	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_dependencyPathEdges_noTFIDF_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_dependencyPathEdges_noTFIDF_2',namedCols2)

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
	
	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_dependencyPathEdgesNearEntities_noTFIDF_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_dependencyPathEdgesNearEntities_noTFIDF_2',namedCols2)

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

	colnames = vectorizer.getFeatureNames()

	# As a quick check, we'll confirm that the column means are as expected
	colmeans1 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols1 = { col:round(v,8) for col,v in zip(colnames,colmeans1) }
	check('test_vectorizer_defaults_triple_1',namedCols1)
	colmeans2 = np.sum(matrix1,axis=0).tolist()[0]
	namedCols2 = { col:round(v,8) for col,v in zip(colnames,colmeans2) }
	check('test_vectorizer_defaults_triple_2',namedCols2)

if __name__ == '__main__':
	test_vectorizer_defaults_triple()

