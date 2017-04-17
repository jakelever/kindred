import kindred

def test_bionlpst():
	trainData = kindred.BioNLPSTData('2016-BB3-event-training')
	devData = kindred.BioNLPSTData('2016-BB3-event-development')
	model = kindred.train(trainData)
	predictedRelations = model.predict(dev_data.getTextAndEntities())
	f1score = kindred.evaluate(dev_data.getRelations(), predictionRelations, metric='f1score')
	assert f1score > 0.5

def test_pubannotation():
	trainData = kindred.PubAnnotationData('2016-SeeDev-binary-training')
	model = kindred.train(trainData)
	text = 'A SeeDev related text goes here'
	predictedRelations = model.predict(text)
	assert len(predicted_relations) == 1

def test_convertTaggedText():
	text = "<drug>Erlotinib</drug> is a common treatment for <cancer>NSCLC</cancer>"
	converted = kindred.utils.convertTaggedText(text)
	
	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(name='drug',text='Erlotinib',start=0,end=10)
	assert entities[1] == kindred.Entity(name='cancer',text='NSCLC',start=0,end=10)

	text = converted.getText()
	assert isinstance(text,unicode) # Python3 issue here
	assert text == u"Erlotinib is a common treatment for NSCLC"

def test_convertedTaggedTextWithRelations():
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>NSCLC</cancer>"
	relations = [ ('treats',1,2) ]

	converted = kindred.utils.convertTaggedTextAndRelations(text,relations)
	assert isinstance(converted,kindred.RelationData)

	assert isinstance(converted,kindred.TextAndEntityData)
	entities = converted.getEntities()
	assert isinstance(entities,list)
	for e in entities:
		assert isinstance(e,kindred.Entity)

	assert entities[0] == kindred.Entity(name='drug',text='Erlotinib',start=0,end=10)
	assert entities[1] == kindred.Entity(name='cancer',text='NSCLC',start=0,end=10)

	text = converted.getText()
	assert isinstance(text,unicode) # Python3 issue here
	assert text == u"Erlotinib is a common treatment for NSCLC"

	assert converted.getRelations() == relations

def test_unicodeCheck():
	assert False

def test_simpleRelationCheck():
	text = "<drug id=1>Erlotinib"
	assert False
	
