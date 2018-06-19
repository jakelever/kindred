
import os
import codecs

import kindred
import bioc

def convertKindredCorpusToBioCCollection(corpus):
	assert isinstance(corpus,kindred.Corpus)
	collection = bioc.BioCCollection()
	for kdoc in corpus.documents:
		assert isinstance(kdoc,kindred.Document)

		biocDoc = bioc.BioCDocument()
		collection.add_document(biocDoc)

		if 'id' in kdoc.metadata:
			biocDoc.id = kdoc.metadata['id']
		biocDoc.infons = kdoc.metadata

		passage = bioc.BioCPassage()
		passage.text = kdoc.text
		passage.offset = 0
		biocDoc.add_passage(passage)

		seenEntityIDs = set()
		kindredID2BiocID = {}
		for e in kdoc.entities:
			assert isinstance(e,kindred.Entity)

			a = bioc.BioCAnnotation()
			a.infons = {'type':e.entityType}
			if e.sourceEntityID is None:
				a.id = str(e.entityID)
			else:
				a.id = e.sourceEntityID

			assert not a.id in seenEntityIDs
			seenEntityIDs.add(a.id)
			kindredID2BiocID[e.entityID] = a.id

			for start,end in e.position:
				l = bioc.BioCLocation(offset=start, length=(end-start))
				a.locations.append(l)

			passage.annotations.append(a)

		for r in kdoc.relations:
			assert isinstance(r,kindred.Relation)
			biocR = bioc.BioCRelation()
			biocR.infons = {'type':r.relationType}
			
			entitiesInRelation = r.entities
			argNames = r.argNames
			if argNames is None:
				argNames = [ "arg%d" % i for i,_ in enumerate(entitiesInRelation) ]

			for argName,entity in zip(argNames,entitiesInRelation):
				node = bioc.BioCNode(role=argName, refid=kindredID2BiocID[entity.entityID])
				biocR.nodes.append(node)

			passage.relations.append(biocR)

	return collection

def saveDocToSTFormat(data,txtPath,a1Path,a2Path):
	assert isinstance(data,kindred.Document)

	with codecs.open(txtPath,'w','utf8') as txtFile, codecs.open(a1Path,'w','utf8') as a1File, codecs.open(a2Path,'w','utf8') as a2File:
		txtFile.write(data.text)
		
		for e in data.entities:
			assert isinstance(e,kindred.Entity)
		
			positions = ";".join("%d %d" % (start,end) for start,end in e.position)
			line = "%s\t%s %s\t%s" % (e.sourceEntityID,e.entityType,positions,e.text)
			a1File.write(line+"\n")
			
		
		for i,r in enumerate(data.relations):
			assert isinstance(r,kindred.Relation)
			
			relationType = r.relationType
			relationEntityIDs = [ entity.sourceEntityID for entity in r.entities ]
			
			if r.argNames is None:
				argNames = [ ("arg%d" % (i+1)) for i in range(len(relationEntityIDs)) ]
			else:
				argNames = r.argNames

			arguments = " ".join(["%s:%s" % (a,b) for a,b in zip(argNames,relationEntityIDs) ])
			line = "R%d\t%s %s" % (i,relationType,arguments)
			a2File.write(line+"\n")

def save(corpus,dataFormat,directory):
	"""
	Save a corpus to a directory
	
	:param corpus: The corpus of documents to save
	:param dataFormat: Format of data to save (only 'standoff' and 'bioc' are supported currently)
	:param directory: Path to directory in which files should be saved
	:type corpus: kindred.Corpus
	:type dataFormat: str
	:type directory: str
	"""
	
	assert dataFormat == 'standoff' or dataFormat == 'bioc'

	assert isinstance(corpus,kindred.Corpus)

	if dataFormat == 'standoff':
		for i,d in enumerate(corpus.documents):
			if d.sourceFilename is None:
				base = "%08d" % i
			else:
				base = d.sourceFilename

			txtPath = os.path.join(directory,'%s.txt' % base)
			a1Path = os.path.join(directory,'%s.a1' % base)
			a2Path = os.path.join(directory,'%s.a2' % base)

			saveDocToSTFormat(d,txtPath,a1Path,a2Path)
	elif dataFormat == 'bioc':
		outFilename = os.path.join(directory, 'collection.bioc.xml')	
		collection = convertKindredCorpusToBioCCollection(corpus)
		#bioc_writer = bioc.BioCWriter(outFilename)
		#bioc_writer.collection = collection
		#bioc_writer.write()
		with bioc.iterwrite(outFilename) as writer:
			for doc in collection.documents:
				writer.writedocument(doc)

	
