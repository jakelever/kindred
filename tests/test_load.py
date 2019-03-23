import os

import kindred
import pytest
import shutil
import tempfile

class TempDir:
	def __init__(self):
		pass

	def __enter__(self):
		self.tempDir = tempfile.mkdtemp()
		return self.tempDir

	def __exit__(self, type, value, traceback):
		shutil.rmtree(self.tempDir)

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.position == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())
	
def test_loadStandoffFile_binary():
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data','example.txt')

	corpus = kindred.load('standoff',txtPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
def test_loadStandoffFile_triple():
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data_triple','example.txt')

	corpus = kindred.load('standoff',txtPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='EGFR',expectedPos=[(13,17)],expectedSourceEntityID="T2")
	assertEntity(entities[2],expectedType='disease',expectedText='NSCLC',expectedPos=[(49,54)],expectedSourceEntityID="T3")
	assert relations == [kindred.Relation('druginfo',[sourceEntityIDsToEntity["T3"],sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['disease','drug','gene'])], "(%s) not as expected" % relations

def test_loadSimpleTagFile():
	scriptDir = os.path.dirname(__file__)
	path = os.path.join(scriptDir,'data','example.simple')

	corpus = kindred.load(dataFormat='simpletag',path=path)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
def test_loadJsonFile():
	scriptDir = os.path.dirname(__file__)
	jsonPath = os.path.join(scriptDir,'data','example.json')

	corpus = kindred.load(dataFormat='json',path=jsonPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_loadBiocFile():
	scriptDir = os.path.dirname(__file__)
	xmlPath = os.path.join(scriptDir,'data','example.bioc.xml')

	corpus = kindred.load(dataFormat='biocxml',path=xmlPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
	
def test_loadStandoffFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.load(dataFormat='standoff',path=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	

def test_loadSimpleTagFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.load(dataFormat='simpletag',path=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
def test_loadJsonFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.load(dataFormat='json',path=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_loadBiocFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.load(dataFormat='biocxml',path=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	doc = corpus.documents[0]
	
	assert isinstance(doc,kindred.Document)
	entities = doc.entities
	relations = doc.relations

	sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_loadEmptyDirectory():
	with TempDir() as tempDir:
		for dataformat in ['standoff','simpletag','json','biocxml']:
			with pytest.raises(RuntimeError) as excinfo:
				corpus = kindred.load(dataformat,tempDir)
			expectedError = 'No documents loaded from directory (%s). Are you sure this directory contains the corpus (format: %s)' % (tempDir.rstrip('/'),dataformat)
			assert excinfo.value.args == (expectedError ,)

def test_iterLoadBiocFile():
	text = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	docsToCreate = 100

	with TempDir() as tempDir:

		singleDoc = corpus.documents[0]
		corpus.documents = [ singleDoc for _ in range(docsToCreate) ]

		tempFile = os.path.join(tempDir,'corpus.bioc.xml')
		kindred.save(corpus,'biocxml',tempFile)

		totalDocCount = 0
		for corpus in kindred.iterLoad('biocxml',tempFile,corpusSizeCutoff=3):
			assert isinstance(corpus,kindred.Corpus)

			assert len(corpus.documents) <= 25
			totalDocCount += len(corpus.documents)

			for doc in corpus.documents:
				assert isinstance(doc,kindred.Document)
				entities = doc.entities
				relations = doc.relations

				sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

				assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
				assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
				assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

		assert totalDocCount == docsToCreate

def test_iterLoadBiocDir():
	text = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	docsToCreate = 100

	with TempDir() as tempDir:

		singleDoc = corpus.documents[0]
		corpus.documents = [ singleDoc for _ in range(docsToCreate) ]

		tempFile = os.path.join(tempDir,'corpus.bioc.xml')
		kindred.save(corpus,'biocxml',tempFile)

		totalDocCount = 0
		for corpus in kindred.iterLoad('biocxml',tempDir,corpusSizeCutoff=3):
			assert isinstance(corpus,kindred.Corpus)

			assert len(corpus.documents) <= 25
			totalDocCount += len(corpus.documents)

			for doc in corpus.documents:
				assert isinstance(doc,kindred.Document)
				entities = doc.entities
				relations = doc.relations

				sourceEntityIDsToEntity = { entity.sourceEntityID:entity for entity in entities }

				assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
				assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
				assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntity["T1"],sourceEntityIDsToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

		assert totalDocCount == docsToCreate

if __name__ == '__main__':
	test_loadBiocFile()
	

