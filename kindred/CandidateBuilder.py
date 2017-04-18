
import kindred
from kindred.Parser import Parser

class CandidateBuilder:
	def __init__(self):
		pass
	
	def build(self,trainData):
		assert isinstance(trainData,list)
		for t in trainData:
			assert isinstance(t,kindred.RelationData) or isinstance(t,kindred.TextAndEntityData)
			
		parser = Parser()
		sentencesWithEntities = parser.parse(trainData)
		
		assert isinstance(sentencesWithEntities,list)
		for p in sentencesWithEntities:
			assert isinstance(parse,kindred.ParsedSentenceWithEntities)
		assert len(sentencesWithEntities) == 1
		
		
		
		examples = []
		classes = []
		relTypes = []
		
		for sentenceWithEntities in sentencesWithEntities:
			
			positiveRelations = {}
			positiveRelationsProcessed = []
			for (relName,id1,id2) in relations:
				sentenceid1,locs1 = findTrigger(sentenceData,id1)
				sentenceid2,locs2 = findTrigger(sentenceData,id2)

				type1 = sentenceData[sentenceid1].locsToTriggerTypes[tuple(locs1)]
				type2 = sentenceData[sentenceid2].locsToTriggerTypes[tuple(locs2)]
				#if sentenceid1 != sentenceid2:
				#	print "WARNING: Relation split across sentences (%s and %s)" % (id1,id2)
				#	continue
				#sentenceid = sentenceid1

				#print "POSITIVE", relName, type1, type2

				#key = (relName,type1,type2)
				#key = relName

				#print relName
				if not relName in targetRelations:
					continue

				key = (sentenceid1,tuple(locs1),sentenceid2,tuple(locs2))
				classid = targetRelations[relName]
				positiveRelations[key] = classid
				#positiveRelations[key] = True

					
			# Now we go through all sentences and create examples for all possible token combinations
			# Then check if any are already marked as positive and add to the appropriate list of examples
			for sentenceid1 in range(len(sentenceData)):
				for sentenceid2 in range(max(sentenceid1-sentenceRange,0),min(sentenceid1+sentenceRange+1,len(sentenceData))):
					#print sentenceid1,sentenceid2
					sentence1,sentence2 = sentenceData[sentenceid1],sentenceData[sentenceid2]
				
					eventLocsAndTypes1 = [ (sentence1.predictedEntityLocs[id],sentence1.predictedEntityTypes[id]) for id in sentence1.predictedEntityTypes ]
					argsLocsAndTypes1 = [ (sentence1.knownEntityLocs[id],sentence1.knownEntityTypes[id]) for id in sentence1.knownEntityTypes ]
					possibleLocsAndTypes1 = eventLocsAndTypes1 + argsLocsAndTypes1
					
					eventLocsAndTypes2 = [ (sentence2.predictedEntityLocs[id],sentence2.predictedEntityTypes[id]) for id in sentence2.predictedEntityTypes ]
					argsLocsAndTypes2 = [ (sentence2.knownEntityLocs[id],sentence2.knownEntityTypes[id]) for id in sentence2.knownEntityTypes ]
					possibleLocsAndTypes2 = eventLocsAndTypes2 + argsLocsAndTypes2
								
					for (locs1,type1),(locs2,type2) in itertools.product(possibleLocsAndTypes1,possibleLocsAndTypes2):
						if sentenceid1 == sentenceid2 and locs1 == locs2:
							continue

						key = (type1,type2)
						if doFiltering and not key in targetArguments:
							continue

						#print "POTENTIAL", type1, type2

						key = (sentenceid1,tuple(locs1),sentenceid2,tuple(locs2))
						example = Example(filename, sentenceData, arg1_sentenceid=sentenceid1, arg1_locs=locs1, arg2_sentenceid=sentenceid2, arg2_locs=locs2)
						examples.append(example)

						thisClass = 0
						if key in positiveRelations:
							thisClass = positiveRelations[key]
							#thisClass = 1
							positiveRelationsProcessed.append(key)
						classes.append(thisClass)
						relTypes.append((type1,type2))
							
			#print filename
			for key in positiveRelations:
				#assert key in allArgTriggerLocsProcessed, 'Unprocessed event trigger found: ' + str(key)
				if not key in positiveRelationsProcessed:
					print 'WARNING: Unprocessed argument trigger found: %s in file: %s' % (str(key), filename) 
				
		#for c,e in zip(classes,examples):
		#	print c,e

		#sys.exit(0)
					
		return classes, examples, relTypes