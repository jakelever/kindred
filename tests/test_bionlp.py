
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
	assert entityCount == 1224
	assert relationCount == 327
		


if __name__ == '__main__':
	test_loadBioNLP_BB3_event_train()
