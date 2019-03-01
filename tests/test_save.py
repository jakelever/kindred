import os
import tempfile
import shutil

import kindred
import pytest

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
	
def checkRelationAnnotations(filename):
	"""
	Checks that the relation indices are incrementally increasing from 1 (so it goes R1,R2,R3,etc).
	"""
	expected = 1
	with open(filename) as f:
		for line in f:
			if line.startswith('R'): # It's a relation
				relIndex = line.split('\t')[0].replace('R','')
				assert expected == int(relIndex), 'Relation indices must increment from 1 in a standoff file'
				expected += 1

def test_saveStandoffFile_fromSimpleTag():
	text = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	with TempDir() as tempDir:
		kindred.save(corpus,'standoff',tempDir)

		for filename in os.listdir(tempDir):
			if filename.endswith('.a2'):
				checkRelationAnnotations(os.path.join(tempDir,filename))

		loadedCorpus = kindred.load('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.entities
	relations = loadedDoc.relations

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_saveStandoffFile_noSourceEntityID():
	text = 'The <disease>colorectal cancer</disease> is bad.'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	with TempDir() as tempDir:
		with pytest.raises(AssertionError) as excinfo:   
			kindred.save(corpus,'standoff',tempDir)
		assert excinfo.value.args[0] == 'Entities must have a sourceEntityID (e.g. T1) to be saved in the standoff format'
	
def test_saveBiocFile_fromSimpleTag():
	text = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	with TempDir() as tempDir:
		tempFile = os.path.join(tempDir,'corpus.bioc.xml')
		kindred.save(corpus,'biocxml',tempFile)
		
		loadedCorpus = kindred.load('biocxml',tempFile)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.entities
	relations = loadedDoc.relations

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_saveStandoffFile_fromSimpleTag_triple():
	text = '<drug id="T1">Erlotinib</drug>, a <gene id="T2">EGFR</gene> inhibitor is commonly used for <disease id="T3">NSCLC</disease> patients. <relation type="druginfo" drug="T1" gene="T2" disease="T3" />'
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	with TempDir() as tempDir:
		kindred.save(corpus,'standoff',tempDir)
		
		for filename in os.listdir(tempDir):
			if filename.endswith('.a2'):
				checkRelationAnnotations(os.path.join(tempDir,filename))

		loadedCorpus = kindred.load('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.entities
	relations = loadedDoc.relations

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='EGFR',expectedPos=[(13,17)],expectedSourceEntityID="T2")
	assertEntity(entities[2],expectedType='disease',expectedText='NSCLC',expectedPos=[(49,54)],expectedSourceEntityID="T3")
	assert relations == [kindred.Relation('druginfo',[sourceEntityIDToEntity["T3"],sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['disease','drug','gene'])], "(%s) not as expected" % relations
	
def test_saveStandoffFile():
	text = "The colorectal cancer was caused by mutations in APC"
	e1 = kindred.Entity(entityType="disease",text="colorectal cancer",position=[(4, 21)],sourceEntityID="T1")
	e2 = kindred.Entity(entityType="gene",text="APC",position=[(49, 52)],sourceEntityID="T2")
	rel = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=['obj','subj'])
	doc = kindred.Document(text,[e1,e2],[rel])
	corpus = kindred.Corpus()
	corpus.addDocument(doc)

	with TempDir() as tempDir:
		kindred.save(corpus,'standoff',tempDir)
		
		for filename in os.listdir(tempDir):
			if filename.endswith('.a2'):
				checkRelationAnnotations(os.path.join(tempDir,filename))

		loadedCorpus = kindred.load('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.entities
	relations = loadedDoc.relations

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
def test_saveStandoffFile_noArgNames():
	text = "The colorectal cancer was caused by mutations in APC"
	e1 = kindred.Entity(entityType="disease",text="colorectal cancer",position=[(4, 21)],sourceEntityID="T1")
	e2 = kindred.Entity(entityType="gene",text="APC",position=[(49, 52)],sourceEntityID="T2")
	rel = kindred.Relation(relationType="causes",entities=[e1,e2])
	doc = kindred.Document(text,[e1,e2],[rel])
	corpus = kindred.Corpus()
	corpus.addDocument(doc)

	with TempDir() as tempDir:
		kindred.save(corpus,'standoff',tempDir)
		
		for filename in os.listdir(tempDir):
			if filename.endswith('.a2'):
				checkRelationAnnotations(os.path.join(tempDir,filename))

		loadedCorpus = kindred.load('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.entities
	relations = loadedDoc.relations

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['arg1','arg2'])], "(%s) not as expected" % relations
	
def test_saveBB3Data():
	corpus = kindred.bionlpst.load('2016-BB3-event-train')
	assert isinstance(corpus,kindred.Corpus)

	with TempDir() as tempDir:
		kindred.save(corpus,'standoff',tempDir)
		
		for filename in os.listdir(tempDir):
			if filename.endswith('.a2'):
				checkRelationAnnotations(os.path.join(tempDir,filename))

		loadedCorpus = kindred.load('standoff',tempDir)
		assert len(corpus.documents) == len(loadedCorpus.documents)
	
def test_saveStandoffFile_SeparateSentences():
	texts = ['The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />','<disease id="T1">Li-Fraumeni</disease> was caused by mutations in <gene id="T2">P53</gene><relation type="causes" subj="T2" obj="T1" />']
	corpus = kindred.Corpus()
	for t in texts:
		doc = kindred.Document(t,loadFromSimpleTag=True)
		corpus.addDocument(doc)

	with TempDir() as tempDir:
		kindred.save(corpus,'standoff',tempDir)
		
		for filename in os.listdir(tempDir):
			if filename.endswith('.a2'):
				checkRelationAnnotations(os.path.join(tempDir,filename))

		loadedCorpus = kindred.load('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 2
	
	data = loadedCorpus.documents[0]
	assert isinstance(data,kindred.Document)
	entities = data.entities
	relations = data.relations
	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }
	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	data = loadedCorpus.documents[1]
	assert isinstance(data,kindred.Document)
	entities = data.entities
	relations = data.relations
	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }
	assertEntity(entities[0],expectedType='disease',expectedText='Li-Fraumeni',expectedPos=[(0,11)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='P53',expectedPos=[(39,42)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDToEntity["T1"],sourceEntityIDToEntity["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
if __name__ == '__main__':
	#test_saveStandoffFile_PredictedRelations()
	test_saveBB3Data()

