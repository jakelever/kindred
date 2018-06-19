import kindred

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.position == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

def test_convertTaggedText():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = "<drug>Erlotinib</drug> is a common treatment for <cancer>NSCLC</cancer>"
	converted = kindred.Document(text,loadFromSimpleTag=True)
	
	assert isinstance(converted,kindred.Document)
	entities = converted.entities
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID=1)
	assertEntity(entities[1],expectedType='cancer',expectedText='NSCLC',expectedPos=[(36,41)],expectedSourceEntityID=2)

	text = converted.text
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for NSCLC"
	
	
def test_convertTaggedTextWithSplitEntities():
	#text = 'The <drug><disease>Erlotinib</disease></drug> is a common treatment for <cancer>NSCLC</cancer> patients'
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">lung</cancer> and unknown <cancer id="2">cancers</cancer>'
	converted = kindred.Document(text,loadFromSimpleTag=True)
	
	assert isinstance(converted,kindred.Document)
	entities = converted.entities
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID='1')
	assertEntity(entities[1],expectedType='cancer',expectedText='lung cancers',expectedPos=[(36,40), (53,60)],expectedSourceEntityID='2')

	text = converted.text
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == "Erlotinib is a common treatment for lung and unknown cancers"

def test_convertedTaggedTextWithRelations():
	text = '<drug id="5">Erlotinib</drug> is a common treatment for <cancer id="6">NSCLC</cancer><relation type="treats" subj="5" obj="6" />'

	converted = kindred.Document(text,loadFromSimpleTag=True)
	assert isinstance(converted,kindred.Document)

	entities = converted.entities
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assertEntity(entities[0],expectedType='drug',expectedText='Erlotinib',expectedPos=[(0,9)],expectedSourceEntityID='5')
	assertEntity(entities[1],expectedType='cancer',expectedText='NSCLC',expectedPos=[(36,41)],expectedSourceEntityID='6')

	text = converted.text
	#assert isinstance(text,unicode) # Python3 issue here
	assert text == u"Erlotinib is a common treatment for NSCLC"

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in converted.entities }

	assert converted.relations == [kindred.Relation('treats',[sourceEntityIDToEntity['6'],sourceEntityIDToEntity['5']],['obj','subj'])]

if __name__ == '__main__':
	test_convertedTaggedTextWithRelations()
	
