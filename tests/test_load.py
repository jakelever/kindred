import os

import kindred

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.pos == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())
	
def test_loadStandoffFile():
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data','example.txt')
	a1Path = os.path.join(scriptDir,'data','example.a1')
	a2Path = os.path.join(scriptDir,'data','example.a2')

	dataList = kindred.load(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path)
	
	assert isinstance(dataList,list)
	assert len(dataList) == 1
	data = dataList[0]
	
	assert isinstance(data,kindred.RelationData)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	

def test_loadSimpleTagFile():
	scriptDir = os.path.dirname(__file__)
	path = os.path.join(scriptDir,'data','example.simple')

	dataList = kindred.load(dataFormat='simpletag',path=path)
	
	assert isinstance(dataList,list)
	assert len(dataList) == 1
	data = dataList[0]
	
	assert isinstance(data,kindred.RelationData)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
	
def test_loadJsonFile():
	scriptDir = os.path.dirname(__file__)
	jsonPath = os.path.join(scriptDir,'data','example.json')

	dataList = kindred.load(dataFormat='json',path=jsonPath)
	
	assert isinstance(dataList,list)
	assert len(dataList) == 1
	data = dataList[0]
	
	assert isinstance(data,kindred.RelationData)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations

	
if __name__ == '__main__':
	test_loadJsonFile()

