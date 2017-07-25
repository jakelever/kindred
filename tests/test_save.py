import os
import tempfile
import shutil

import kindred

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.position == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())
	
def test_saveStandoffFile_fromSimpleTag():
	text = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />'
	corpus = kindred.Corpus()
	doc = kindred.Document(text)
	corpus.addDocument(doc)

	tempDir = tempfile.mkdtemp()

	kindred.save(corpus,'standoff',tempDir)

	loadedCorpus = kindred.loadDir('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.getEntities()
	relations = loadedDoc.getRelations()

	sourceEntityIDsToEntityIDs = loadedDoc.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	shutil.rmtree(tempDir)

def test_saveStandoffFile():
	text = "The colorectal cancer was caused by mutations in APC"
	e1 = kindred.Entity(entityType="disease",text="colorectal cancer",position=[(4, 21)],sourceEntityID="T1")
	e2 = kindred.Entity(entityType="gene",text="APC",position=[(49, 52)],sourceEntityID="T2")
	rel = kindred.Relation(relationType="causes",entityIDs=[e1.entityID,e2.entityID],argNames=['obj','subj'])
	doc = kindred.Document(text,[e1,e2],[rel],relationsUseSourceIDs=False)
	corpus = kindred.Corpus()
	corpus.addDocument(doc)

	tempDir = tempfile.mkdtemp()

	kindred.save(corpus,'standoff',tempDir)

	loadedCorpus = kindred.loadDir('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.getEntities()
	relations = loadedDoc.getRelations()

	sourceEntityIDsToEntityIDs = loadedDoc.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	shutil.rmtree(tempDir)
	
def test_saveStandoffFile_noArgNames():
	text = "The colorectal cancer was caused by mutations in APC"
	e1 = kindred.Entity(entityType="disease",text="colorectal cancer",position=[(4, 21)],sourceEntityID="T1")
	e2 = kindred.Entity(entityType="gene",text="APC",position=[(49, 52)],sourceEntityID="T2")
	rel = kindred.Relation(relationType="causes",entityIDs=[e1.entityID,e2.entityID])
	doc = kindred.Document(text,[e1,e2],[rel],relationsUseSourceIDs=False)
	corpus = kindred.Corpus()
	corpus.addDocument(doc)

	tempDir = tempfile.mkdtemp()

	kindred.save(corpus,'standoff',tempDir)

	loadedCorpus = kindred.loadDir('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.getEntities()
	relations = loadedDoc.getRelations()

	sourceEntityIDsToEntityIDs = loadedDoc.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['arg1','arg2'])], "(%s) not as expected" % relations
	
	shutil.rmtree(tempDir)

def test_saveStandoffFile_predictedRels_noArgNames():
	text = "The colorectal cancer was caused by mutations in APC"
	e1 = kindred.Entity(entityType="disease",text="colorectal cancer",position=[(4, 21)],sourceEntityID="T1")
	e2 = kindred.Entity(entityType="gene",text="APC",position=[(49, 52)],sourceEntityID="T2")
	doc = kindred.Document(text,[e1,e2])
	corpus = kindred.Corpus()
	corpus.addDocument(doc)

	tempDir = tempfile.mkdtemp()

	rel = kindred.Relation(relationType="causes",entityIDs=[e1.entityID,e2.entityID])
	kindred.save(corpus,'standoff',tempDir,predictedRelations=[rel])

	loadedCorpus = kindred.loadDir('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 1
	loadedDoc = loadedCorpus.documents[0]
	
	assert isinstance(loadedDoc,kindred.Document)
	entities = loadedDoc.getEntities()
	relations = loadedDoc.getRelations()

	sourceEntityIDsToEntityIDs = loadedDoc.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['arg1','arg2'])], "(%s) not as expected" % relations
	
	shutil.rmtree(tempDir)

def test_saveBB3Data():
	corpus = kindred.bionlpst.load('2016-BB3-event-train')
	assert isinstance(corpus,kindred.Corpus)

	tempDir = tempfile.mkdtemp()

	kindred.save(corpus,'standoff',tempDir)

	loadedCorpus = kindred.loadDir('standoff',tempDir)
	assert len(corpus.documents) == len(loadedCorpus.documents)

	shutil.rmtree(tempDir)
	
def test_saveStandoffFile_SeparateSentences():
	texts = ['The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />','<disease id="T1">Li-Fraumeni</disease> was caused by mutations in <gene id="T2">P53</gene><relation type="causes" subj="T2" obj="T1" />']
	corpus = kindred.Corpus()
	for t in texts:
		doc = kindred.Document(t)
		corpus.addDocument(doc)

	tempDir = tempfile.mkdtemp()

	kindred.save(corpus,'standoff',tempDir)

	loadedCorpus = kindred.loadDir('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 2
	
	data = loadedCorpus.documents[0]
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()
	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()
	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	data = loadedCorpus.documents[1]
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()
	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()
	assertEntity(entities[0],expectedType='disease',expectedText='Li-Fraumeni',expectedPos=[(0,11)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='P53',expectedPos=[(39,42)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	shutil.rmtree(tempDir)
	
	
	
def test_saveStandoffFile_PredictedRelations():
	texts = ['The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />','<disease id="T1">Li-Fraumeni</disease> was caused by mutations in <gene id="T2">P53</gene><relation type="causes" subj="T2" obj="T1" />']
	corpus = kindred.Corpus()
	for t in texts:
		doc = kindred.Document(t)
		corpus.addDocument(doc)
	
	predictedRelations = []
	# Rip out the relations and save as predicted ones
	for d in corpus.documents:
		predictedRelations += d.relations
		d.relations = []

	tempDir = tempfile.mkdtemp()

	kindred.save(corpus,'standoff',tempDir,predictedRelations=predictedRelations)

	loadedCorpus = kindred.loadDir('standoff',tempDir)

	assert isinstance(loadedCorpus,kindred.Corpus)
	assert len(loadedCorpus.documents) == 2
	
	data = loadedCorpus.documents[0]
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()
	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()
	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	data = loadedCorpus.documents[1]
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()
	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()
	assertEntity(entities[0],expectedType='disease',expectedText='Li-Fraumeni',expectedPos=[(0,11)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='P53',expectedPos=[(39,42)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	shutil.rmtree(tempDir)
	
	
if __name__ == '__main__':
	#test_saveStandoffFile_PredictedRelations()
	test_saveBB3Data()

