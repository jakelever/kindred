import tempfile

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

from kindred.DataLoad import loadDataFromSTFormat_Directory

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.pos == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def test_loadST():
	tempDir = tempfile.mkdtemp()

	txtPath = "%s/0.txt" % tempDir
	a1Path = "%s/0.a1" % tempDir
	a2Path = "%s/0.a2" % tempDir

	with open(txtPath,'w') as txtFile, open(a1Path,'w') as a1File, open(a2Path,'w') as a2File:
		txtFile.write("Erlotinib is a common treatment for NSCLC\n")
		a1File.write("T1\tdrug 0 9\tErlotinib\n")
		a1File.write("T2\tcancer 36 41\tNSCLC\n")
		a2File.write("E1\ttreats arg1:T1 arg2:T2")

	data = loadDataFromSTFormat_Directory(tempDir)
	assert len(data) == 1
	entities = data[0].getEntities()
	relations = data[0].getRelations()

	sourceEntityIDsToEntityIDs = data[0].getSourceEntityIDsToEntityIDs()

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID="T1")
	assertEntity(entities[1],expectedType='cancer',expectedText='NSCLC',expectedPos=[(36,41)],expectedSourceEntityID="T2")
	assert relations == [kindred.Relation('treats',[sourceEntityIDsToEntityIDs["T1"],sourceEntityIDsToEntityIDs["T2"]],['arg1','arg2'])]

if __name__ == '__main__':
	test_loadST()

