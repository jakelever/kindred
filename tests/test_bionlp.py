
import kindred
from kindred.BioNLPSTData import loadBioNLPData

def test_loadBioNLP_BB3_event_train():
	data = loadBioNLPData('2016-BB3-event-training')

	assert isinstance(data,list)
	for d in data:
		assert isinstance(d,kindred.RelationData)

	firstFile = data[0]
	print firstFile.getSourceFilename()
	print firstFile.getText()
	print firstFile.getEntities()
	print firstFile.getRelations()


if __name__ == '__main__':
	test_loadBioNLP_BB3_event_train()
