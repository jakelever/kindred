import os
import tempfile

import kindred

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.position == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())
	
def _saveStandoffFile():
	text = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene><relation type="causes" subj="T2" obj="T1" />'
	data = kindred.RelationData(text)
	dataList = [data]

	tempDir = tempfile.mkdtemp()
	#txtPath = os.path.join(tempDir,'test.txt')
	#a1Path = os.path.join(tempDir,'test.a1')
	#a2Path = os.path.join(tempDir,'test.a2')

	kindred.save(dataList,'standoff',tempDir)

	loadedList = kindred.load(dataFormat='standoff',txtPath=txtPath,a1Path=a1Path,a2Path=a2Path)

	assert isinstance(loadedList,list)
	assert len(loadedList) == 1
	data = loadedList[0]
	
	assert isinstance(data,kindred.RelationData)
	entities = data.getEntities()
	relations = data.getRelations()

	sourceEntityIDsToEntityIDs = data.getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='disease',expectedText='colorectal cancer',expectedPos=[(4,21)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='gene',expectedText='APC',expectedPos=[(49,52)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('causes',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['obj','subj'])], "(%s) not as expected" % relations
	
if __name__ == '__main__':
	test_saveStandoffFile()

