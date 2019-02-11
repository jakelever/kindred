import kindred
from collections import OrderedDict,defaultdict
import six

# Colors to use for output sentences with annotation
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class RESPONSE:
	POSITIVE = 1
	NEGATIVE = 0
	ENTITYERROR = -1
		
	TABLE = {'y':POSITIVE,'n':NEGATIVE,'x':ENTITYERROR}


def manuallyAnnotate(corpus,candidateRelations):
	"""
	Provides a method for basic manual annotation of a series of candidate relations. Deals with a corpus, sentence by sentence, and prompts the user to annotate each candidate relation in turn. Can be exited before completion of the full list and the resulting annotations are split into an annotated corpus and unannotated corpus. Each document in the new corpora are individual sentences.
	
	:param corpus: Corpus of text for annotation
	:param candidateRelations: List of candidate relations (created using CandidateBuilder) to manually review and annotate
	:type corpus: kindred.Corpus
	:type candidateRelations: List of kindred.CandidateRelation
	:return: a tuple of an annotated corpus and unannotated corpus
	:rtype: two kindred.Corpus
	"""

	annotatedCorpus = kindred.Corpus()
	unannotatedCorpus = kindred.Corpus()

	options = OrderedDict()
	options['x'] = 'Done'
	options['0'] = 'None'

	print()
	print("For each sentence, choose an existing option or type the name of a new annotation")
	
	endAnnotation = False
	crCounter = 0
	#for sentence,crsInSentence in groupedBySentences.items():
	for doc in corpus.documents:
		docSentences = set(doc.sentences)
		crsInDoc = [ cr for cr in candidateRelations if cr.sentence in docSentences ]

		doc = kindred.Document(doc.text,doc.entities,[])

		if not endAnnotation:
			for candidateRelation in crsInDoc:
				crCounter += 1

				sentence = candidateRelation.sentence
				sentenceStart = sentence.tokens[0].startPos

				e1,e2 = candidateRelation.entities

				assert len(e1.position) == 1, 'Annotator cannot currently deal with non-continuous entities'
				assert len(e2.position) == 1, 'Annotator cannot currently deal with non-continuous entities'
				start1,end1 = e1.position[0]
				start2,end2 = e2.position[0]

				start1,end1 = start1-sentenceStart,end1-sentenceStart
				start2,end2 = start2-sentenceStart,end2-sentenceStart

				charByChar = list(candidateRelation.sentence.text)
				charByChar[start1] = bcolors.FAIL + charByChar[start1]
				charByChar[end1-1] += bcolors.ENDC
				charByChar[start2] = bcolors.OKGREEN + charByChar[start2]
				charByChar[end2-1] += bcolors.ENDC
				
				sentence = "".join(charByChar)

				print()
				print('#'*30 + " (%d/%d)" % (crCounter,len(candidateRelations)))
				print(sentence)

				optionTxt = " ".join("%s:%s" % (key,value) for key,value in options.items())

				response = None
				while not response:
					response = six.moves.input('%s ? ' % optionTxt).strip()

				if response == 'x':
					endAnnotation = True
					break
				elif response and not response in optionTxt:
					newKey = str(len(options)-1)
					options[newKey] = response
				else:
					response = options[response]

				if response != 'None':
					r = kindred.Relation(response,candidateRelation.entities)
					doc.addRelation(r)

		if endAnnotation:
			# Annotation is incomplete, so wipe any previous annotation on this sentence
			doc.relations = []
			unannotatedCorpus.addDocument(doc)
		else:
			annotatedCorpus.addDocument(doc)

	return annotatedCorpus,unannotatedCorpus


