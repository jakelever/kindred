import os

import kindred

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.pos == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def test_loadST():
	scriptDir = os.path.dirname(__file__)
	txtPath = os.path.join(scriptDir,'data','example.txt')
	a1Path = os.path.join(scriptDir,'data','example.a1')
	a2Path = os.path.join(scriptDir,'data','example.a2')

	data = kindred.load(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path)
	
	assert len(data) == 1
	entities = data[0].getEntities()
	relations = data[0].getRelations()

	sourceEntityIDsToEntityIDs = data[0].getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='cancer',expectedText='NSCLC',expectedPos=[(36,41)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('treats',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['arg1','arg2'])]

if __name__ == '__main__':
	test_loadST()

