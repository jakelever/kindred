import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

def test_convertTaggedText():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = "<drug>Erlotinib</drug> is a common treatment for <cancer>NSCLC</cancer>"
	converted = kindred.TextAndEntityData(text)
	
	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=1,text='Erlotinib',pos=[(0,9)]), "(%s) not as expected" % (entities[0].__str__())
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=2,text='NSCLC',pos=[(36,41)]), "(%s) not as expected" % (entities[1].__str__())

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for NSCLC"
	
	
def test_convertTaggedTextWithSplitEntities():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>lung</cancer> and unknown <cancer id=2>cancers</cancer>"
	converted = kindred.TextAndEntityData(text)
	
	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=1,text='Erlotinib',pos=[(0,9)])
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=2,text='lung cancers',pos=[(36,40), (53,60)])

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for lung and unknown cancers"

def test_convertedTaggedTextWithRelations():
	text = "<drug id=5>Erlotinib</drug> is a common treatment for <cancer id=6>NSCLC</cancer>"
	relations = [ ('treats',5,6) ]

	converted = kindred.RelationData(text,relations)
	assert isinstance(converted,kindred.RelationData)

	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(entityType='drug',entityID=5,text='Erlotinib',pos=[(0,9)])
	assert entities[1] == kindred.Entity(entityType='cancer',entityID=6,text='NSCLC',pos=[(36,41)])

	text = converted.getText()
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == u"Erlotinib is a common treatment for NSCLC"

	assert converted.getRelations() == relations
