import kindred
import os

def isNumber(s):
	"""
	Check if a string is a numeric (int or float) value
	"""
	try:
		float(s)
		return True
	except ValueError:
		return False

class QuantityRecognizer:
	"""
	Example of a custom entity recognizer that will annotate any numbers that it finds in a sentence
	"""

	def __init__(self):
		pass

	def annotate(self,corpus):
		"""
		Annotate a corpus for numerical values

		:param corpus: Corpus to annotate
		:type corpus: kindred.Corpus
		"""

		assert corpus.parsed == True, "Corpus must already be parsed before entity recognition"

		for doc in corpus.documents:
			entityCount = len(doc.entities)
			for sentence in doc.sentences:
				words = [ t.word for t in sentence.tokens ]
				
				for i,t in enumerate(sentence.tokens):
					if not isNumber(t.word):
						continue
					
					sourceEntityID = "T%d" % (entityCount+1)
					text = doc.text[t.startPos:t.endPos]
					loc = [i]

					e = kindred.Entity('quantity',text,[(t.startPos,t.endPos)],sourceEntityID=sourceEntityID)
					doc.addEntity(e)
					sentence.addEntityAnnotation(e,loc)
					entityCount += 1


if __name__ == '__main__':

	text = "We measured the voltage at 5 volts. "
	text += "We tested our 5 samples for current. "
	text += "Blah et al calculated a current of 3.1 amps. "
	text += "5 of the 8 samples weren't tested for voltage. "
	text += "The mean voltage was 4 V across all of the samples. "
	text += "The current was sampled on March 29. "
	text += "A current of 2.3 amps was measured. "
	text += "The voltage was found to be 2 volts. "

	print("Creating and parsing the sample text")
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	print("Splitting the corpus into sentences so that we can save any annotated sentences and don't need to annotate it all")
	sentenceCorpus = corpus.splitIntoSentences()

	print("Looking for measurement words, e.g. voltage")
	wordlist = { ('voltage',):{('measurement','voltage')}, ('current',):{('measurement','current')} }

	entityRecognizer = kindred.EntityRecognizer(wordlist)
	entityRecognizer.annotate(sentenceCorpus)

	print("Looking for numeric values")
	quantityRecognizer = QuantityRecognizer()
	quantityRecognizer.annotate(sentenceCorpus)

	print("Find every pair of a measurement word and a value")
	candidateBuilder = kindred.CandidateBuilder(acceptedEntityTypes=[('measurement','quantity')])
	candidateRelations = candidateBuilder.build(sentenceCorpus)

	print("Let's annotate a few")
	withRelations,noRelations = kindred.manuallyAnnotate(sentenceCorpus,candidateRelations)

	outDir = 'numericalAnnotations'
	if not os.path.isdir(outDir):
		os.makedirs(outDir)

	print("Saving results to directory...")
	kindred.save(withRelations,'standoff',outDir)

