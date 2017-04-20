
import kindred
from kindred.BioNLPSTData import loadBioNLPData

def test_loadBioNLP_BB3_event_train():
	data = loadBioNLPData('2016-BB3-event-train')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 61
	assert relationCount == 327
	assert entityCount == 1224
		

def test_loadBioNLP_BB3_event_dev():
	data = loadBioNLPData('2016-BB3-event-dev')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 34
	assert relationCount == 223
	assert entityCount == 816

def test_loadBioNLP_BB3_event_test():
	data = loadBioNLPData('2016-BB3-event-test')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 51
	assert relationCount == 0
	assert entityCount == 1246

def test_loadBioNLP_SeeDev_binary_train():
	data = loadBioNLPData('2016-SeeDev-binary-train')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 39
	assert relationCount == 1628
	assert entityCount == 3259

def test_loadBioNLP_SeeDev_binary_dev():
	data = loadBioNLPData('2016-SeeDev-binary-dev')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 19
	assert relationCount == 819
	assert entityCount == 1607

def test_loadBioNLP_SeeDev_binary_test():
	data = loadBioNLPData('2016-SeeDev-binary-test')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 29
	assert relationCount == 0
	assert entityCount == 2216

def test_loadBioNLP_SeeDev_full_train():
	data = loadBioNLPData('2016-SeeDev-full-train')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 39
	assert relationCount == 1169
	assert entityCount == 3259

def test_loadBioNLP_SeeDev_full_dev():
	data = loadBioNLPData('2016-SeeDev-full-dev')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 19
	assert relationCount == 594
	assert entityCount == 1607

def test_loadBioNLP_SeeDev_full_test():
	data = loadBioNLPData('2016-SeeDev-full-test')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	fileCount = len(data)
	entityCount = sum([ len(d.getEntities()) for d in data ])
	relationCount = sum([ len(d.getRelations()) for d in data ])

	assert fileCount == 29
	assert relationCount == 0
	assert entityCount == 2216

if __name__ == '__main__':
	test_loadBioNLP_BB3_event_train()
