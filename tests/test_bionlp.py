
from kindred.BioNLPSTData import loadBioNLPData

def test_loadBioNLP_BB3_event_train():
	data = loadBioNLPData('2016-BB3-event-training')

	print data

if __name__ == '__main__':
	test_loadBioNLP_BB3_event_train()
