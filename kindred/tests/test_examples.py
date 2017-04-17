import kindred

def test_bionlpst():
	train_data = kindred.bionlpst.get_data('2016-BB3-event-training')
	dev_data = kindred.bionlpst.get_data('2016-BB3-event-development')
	model = kindred.train(train_data)
	predicted_relations = model.predict(dev_data.get_text_and_entities())
	f1score = kindred.evaluate(dev_data.get_relations(), prediction_relations, metric='f1score')
	assert f1score > 0.5

def test_pubannotation():
	train_data = kindred.pubannotation.get_data('2016-SeeDev-binary-training')
	model = kindred.train(train_data)
	text = 'A SeeDev related text goes here'
	predicted_relations = model.predict(text)
	assert len(predicted_relations) == 1
