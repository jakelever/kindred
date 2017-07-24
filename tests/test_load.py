import os

import kindred

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.position == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())
	
def test_loadStandoffFile():
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data','example.txt')
	a1Path = os.path.join(scriptDir,'data','example.a1')
	a2Path = os.path.join(scriptDir,'data','example.a2')

	data = kindred.loadDoc(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path)
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	

def test_loadSimpleTagFile():
	scriptDir = os.path.dirname(__file__)
	path = os.path.join(scriptDir,'data','example.simple')

	data = kindred.loadDoc(dataFormat='simpletag',path=path)
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
def test_loadJsonFile():
	scriptDir = os.path.dirname(__file__)
	jsonPath = os.path.join(scriptDir,'data','example.json')

	data = kindred.loadDoc(dataFormat='json',path=jsonPath)
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_loadBiocFile():
	scriptDir = os.path.dirname(__file__)
	jsonPath = os.path.join(scriptDir,'data','example.bioc.xml')

	dataList = kindred.loadDocs(dataFormat='bioc',path=jsonPath)
	
	assert isinstance(dataList,list)
	assert len(dataList) == 1
	data = dataList[0]
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
	
def test_loadStandoffFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.loadDir(dataFormat='standoff',directory=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	data = corpus.documents[0]
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	

def test_loadSimpleTagFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.loadDir(dataFormat='simpletag',directory=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	data = corpus.documents[0]
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
def test_loadJsonFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.loadDir(dataFormat='json',directory=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	data = corpus.documents[0]
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_loadBiocFile_dir():
	scriptDir = os.path.dirname(__file__)
	dataPath = os.path.join(scriptDir,'data')

	corpus = kindred.loadDir(dataFormat='bioc',directory=dataPath)
	
	assert isinstance(corpus,kindred.Corpus)
	assert len(corpus.documents) == 1
	data = corpus.documents[0]
		
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations

def test_loadStandoffFile_missingA2(capfd):
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data_missingA2','example.txt')
	a1Path = os.path.join(scriptDir,'data_missingA2','example.a1')
	a2Path = os.path.join(scriptDir,'data_missingA2','example.a2')
	
	# Run quietly
	data = kindred.loadDoc(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path)

	out, err = capfd.readouterr()
	assert out.strip() == ""
	assert err.strip() == ""
	
	# Run verbose
	data = kindred.loadDoc(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path,verbose=True)

	out, err = capfd.readouterr()
	assert out.strip() == ""
	assert err.strip() == 'Note: No A2 file found : example.a2'
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == []

def test_loadStandoffFile_extraLines(capfd):
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data_extraLines','example.txt')
	a1Path = os.path.join(scriptDir,'data_extraLines','example.a1')
	a2Path = os.path.join(scriptDir,'data_extraLines','example.a2')

	# Run quietly
	data = kindred.loadDoc(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path)

	out, err = capfd.readouterr()
	assert out.strip() == ""
	assert err.strip() == ""
	
	# Run verbose
	data = kindred.loadDoc(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path,verbose=True)

	out, err = capfd.readouterr()
	assert out.strip() == ""
	assert err.strip() == "Unable to process line: *\tEXTRALINE"
	
	assert isinstance(data,kindred.Document)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
if __name__ == '__main__':
	test_loadBiocFile()

