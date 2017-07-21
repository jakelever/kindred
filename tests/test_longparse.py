
import kindred
from kindred.datageneration import generateData,generateTestData

def test_longParse():
	trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)
	parser = kindred.Parser()
	print("A")
	parser.parse(trainCorpus)
	print("B")
	parser.parse(testCorpusGold)

	#trainCorpus, testCorpusGold = generateTestData(positiveCount=100,negativeCount=100)
	#parser = kindred.Parser()
	parser.parse(trainCorpus)
	print("C")
	parser.parse(testCorpusGold)
	print("D")

	trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)
	#parser = kindred.Parser()
	parser.parse(trainCorpus)
	print("E")
	parser.parse(devCorpus)
	print("F")

	#trainCorpus, devCorpus = generateTestData(positiveCount=100,negativeCount=100,relTypes=2)
	#parser = kindred.Parser()
	parser.parse(trainCorpus)
	print("G")
	parser.parse(devCorpus)
	print("H")

if __name__ == '__main__':
	test_longParse()
