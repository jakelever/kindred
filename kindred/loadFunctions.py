import sys
import codecs
import os
import json
import re
from collections import OrderedDict

from xml.dom import minidom

import kindred

import bioc
from future.utils import native

def loadEntity(filename,line,text):
	assert line[0] == 'T', "ERROR in %s. Entity input should start with a T" % filename
	split = line.strip().split('\t')
	assert len(split) == 3, "ERROR in %s" % filename
	entityID = split[0]
	typeInfo = split[1]
	tokens = split[2]
		
	textChunks = []
	typeSpacePos = typeInfo.index(' ')
	typeName = typeInfo[:typeSpacePos]
	positionText = typeInfo[typeSpacePos:]
	positions = []
	for coordinates in positionText.strip().split(';'):
		a,b = coordinates.strip().split(' ')
		a,b = int(a.strip()),int(b.strip())
		textChunk = text[a:b].replace('\n',' ').strip()
		textChunks.append(textChunk)
		positions.append((a,b))
		
	# Check that the tokens match up to the text
	chunkTest = " ".join(textChunks)
	tokensTest = tokens
	chunkTest = re.sub(r'\s\s+', ' ', chunkTest)
	tokensTest = re.sub(r'\s\s+', ' ', tokensTest)
	chunkTest = chunkTest.strip()
	tokensTest = tokensTest.strip()

	assert chunkTest == tokensTest , u"ERROR in " + filename + u"For id=" + entityID + ", tokens '" + tokens.encode('ascii', 'ignore') + "' don't match up with positions: " + str(positions)
	
	entity = kindred.Entity(typeName, tokensTest, positions, entityID)

	return entity
	
def loadRelation(filename,line,ignoreComplexRelations=True):
	assert line[0] == 'E' or line[0] == 'R', "ERROR in %s. Relation input should start with a E or R" % filename
	assert ignoreComplexRelations == True, "ERROR in %s. ignoreComplexRelations must be True as kindred doesn't currently support complex relations" % filename

	split = line.strip().split('\t')
	sourceRelationID = split[0]
	relationInfo = split[1]
	typeSpacePos = relationInfo.index(' ')
	
	relationNameSplit = relationInfo[:typeSpacePos].split(':')
	assert len(relationNameSplit) == 1, "ERROR in %s. Cannot load relations with triggers" % filename
	relationType = relationNameSplit[0]
		
	isComplexRelation = False
	argumentText = relationInfo[typeSpacePos:]
	arguments = []
	for argument in argumentText.strip().split(' '):
		split2 = argument.strip().split(':')
		assert len(split2) == 2, "ERROR in %s" % filename
		tmpArgName = split2[0]
		tmpEntityID = split2[1]

		isComplexRelation = (tmpEntityID[0] == 'R' or tmpEntityID[0] == 'E')

		# We'll skip this relation as
		if ignoreComplexRelations and isComplexRelation:
			break

		assert not isComplexRelation, "ERROR in %s. kindred does not support complex relations (where one relation has another relation as an argument), use ignoreComplexRelations=True to ignore these" % filename

		assert not tmpArgName in arguments, "ERROR in %s" % filename
		arguments.append((tmpArgName,tmpEntityID))

	if ignoreComplexRelations and isComplexRelation:
		return None

	arguments = sorted(arguments)
	sourceEntityIDs = [ entityID for argName,entityID in arguments ]
	argNames = [ argName for argName,entityID in arguments ]

	relationTuple = (sourceRelationID,relationType,sourceEntityIDs,argNames)
	return relationTuple
	
# TODO: Deal with complex relations more clearly
def loadDataFromStandoff(txtFile,ignoreEntities=[],ignoreComplexRelations=True):
	annotationExtensions = ['ann','a1','a2']
	assert ignoreComplexRelations == True, "ignoreComplexRelations must be True as kindred doesn't currently support complex relations"

	with codecs.open(txtFile, "r", "utf-8") as f:
		text = f.read()

	assert txtFile.endswith('.txt')
	base = txtFile[:-4]

	annotationFiles = [ "%s.%s" % (base,ext) for ext in annotationExtensions ]
	annotationFiles = [ filename for filename in annotationFiles if os.path.isfile(filename) ]

	entities = []

	for annotationFile in annotationFiles:
		with codecs.open(annotationFile, "r", "utf-8") as f:
			for line in f:
				if line.startswith('T'):
					entity = loadEntity(annotationFile,line.strip(), text)
					if (not entity is None) and (not entity.entityType in ignoreEntities):
						entities.append(entity)
		
	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	relations = []
	for annotationFile in annotationFiles:
		with codecs.open(annotationFile, "r", "utf-8") as f:
			for line in f:
				if line.startswith('E') or line.startswith('R'):
					relationTuple = loadRelation(annotationFile,line.strip(),ignoreComplexRelations)
					if not relationTuple is None:
						sourceRelationID,relationType,sourceEntityIDs,argNames = relationTuple
						for sourceEntityID in sourceEntityIDs:
							assert sourceEntityID in sourceEntityIDToEntity, "Relation exists that references a non-existent entity (%s) associated with %s" % (sourceEntityID,txtFile)
						entitiesInRelation = [ sourceEntityIDToEntity[sourceEntityID] for sourceEntityID in sourceEntityIDs ]
						relation = kindred.Relation(relationType,entitiesInRelation,argNames,sourceRelationID=sourceRelationID)
						relations.append(relation)

	baseTxtFile = os.path.basename(txtFile)
	baseFilename = baseTxtFile[0:-4]

	combinedData = kindred.Document(text,entities=entities,relations=relations,sourceFilename=baseFilename)
			
	return combinedData

def parsePubAnnotationJSON(data,ignoreEntities=[]):
	entities = []
	relations = []

	if isinstance(data,list):
		assert len(data) == 1 and isinstance(data[0],dict), "PubAnnotation JSON loading expects a dictionary or a list with one dictionary in it"
		data = data[0]
	assert isinstance(data,dict), "PubAnnotation JSON loading expects a dictionary or a list with one dictionary in it"

	text = data['text']
	if 'denotations' in data:
		for d in data['denotations']:
			sourceEntityID = None
			if 'id' in d:
				sourceEntityID = d['id']
			
			entityType = d['obj']
			span = d['span']
			startPos,endPos = span['begin'],span['end']
			position = [(startPos,endPos)]
			entityText = text[startPos:endPos]
			
			if not entityType in ignoreEntities:
				entity = kindred.Entity(entityType,entityText,position,sourceEntityID=sourceEntityID)
				entities.append(entity)

	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	if 'relations' in data:
		for r in data['relations']:
			rID = r['id']
			obj = r['obj']
			relationType = r['pred']
			subj = r['subj']
			
			sourceEntityIDs = [subj,obj]
			argNames = ['subj','obj']
			entitiesInRelation = [ sourceEntityIDToEntity[sourceEntityID] for sourceEntityID in sourceEntityIDs ]
		
			relation = kindred.Relation(relationType,entitiesInRelation,argNames,sourceRelationID=rID)
			relations.append(relation)
	
	expected = ['denotations','divid','modifications','namespaces','project','relations','sourcedb','sourceid','target','text','tracks']
	extraFields = [ k for k in data.keys() if not k in expected]
	assert len(extraFields) == 0, "Found additional unexpected fields (%s) in PubAnnotation JSON" % (",".join(extraFields))
		
	combinedData = kindred.Document(text,entities=entities,relations=relations)

	return combinedData

def loadDataFromPubAnnotationJSON(filename,ignoreEntities=[]):
	with open(filename) as f:
		data = json.load(f)
	parsed = parsePubAnnotationJSON(data,ignoreEntities)
	
	parsed.sourceFilename = os.path.basename(filename)
	
	return parsed
	
def parseSimpleTag_helper(node,currentPosition=0,ignoreEntities=[]):
	text,entities,relationTuples = '',[],[]
	for s in node.childNodes:
		if s.nodeType == s.ELEMENT_NODE:
			insideText,insideEntities,insideRelationTuples = parseSimpleTag_helper(s,currentPosition+len(text))

			if s.tagName == 'relation':
				relationType = s.getAttribute('type')
				arguments = [ (argName,entityID) for argName,entityID in s.attributes.items() if argName != 'type' ]
				arguments = sorted(arguments)
				
				sourceEntityIDs = [ sourceEntityID for argName,sourceEntityID in arguments]
				argNames = [ argName for argName,sourceEntityID in arguments]
				

				relationTuple = (relationType,sourceEntityIDs,argNames)
				relationTuples.append(relationTuple)
			else: # Entity
				entityType = s.tagName
				sourceEntityID = s.getAttribute('id')
				position = [(currentPosition+len(text),currentPosition+len(text)+len(insideText))]

				assert len(insideText) > 0, "Name (text inside tags) is empty for entity of type %s" % entityType

				if not entityType in ignoreEntities:
					e = kindred.Entity(entityType,insideText,position,sourceEntityID=sourceEntityID)
					entities.append(e)
				
			text += insideText
			entities += insideEntities
			relationTuples += insideRelationTuples
		elif s.nodeType == s.TEXT_NODE:
			text += s.nodeValue
			
	return text,entities,relationTuples
	
def mergeEntitiesWithMatchingIDs(unmergedEntities):
	assert isinstance(unmergedEntities,list)

	entityDict = OrderedDict()
	for e in unmergedEntities:
		assert isinstance(e, kindred.Entity)
		if e.sourceEntityID in entityDict:
			entityDict[e.sourceEntityID].text += " " + e.text
			entityDict[e.sourceEntityID].position += e.position
		else:
			entityDict[e.sourceEntityID] = e
			
	return list(entityDict.values())
	
def parseSimpleTag(text,ignoreEntities=[]):
	docText = u"<doc>%s</doc>" % text
	xmldoc = minidom.parseString(docText.encode('utf8'))
	docNode = xmldoc.childNodes[0]
	text,unmergedEntities,relationTuples = parseSimpleTag_helper(docNode,ignoreEntities=ignoreEntities)
	
	missingSourceEntityID = [ e.sourceEntityID == '' for e in unmergedEntities ]
	assert all(missingSourceEntityID) or (not any(missingSourceEntityID)), 'All entities or none (not some) should be given IDs'
	assert (not any(missingSourceEntityID)) or len(relationTuples) == 0, "Cannot include relations with no-ID entities"
	
	if all(missingSourceEntityID):
		for i,e in enumerate(unmergedEntities):
			e.sourceEntityID = i+1
					
	entities = mergeEntitiesWithMatchingIDs(unmergedEntities)
		
	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	relations = []
	for relationType,sourceEntityIDs,argNames in relationTuples:
		assert len(sourceEntityIDs) == len(argNames)
		entitiesInRelation = [ sourceEntityIDToEntity[sourceEntityID] for sourceEntityID in sourceEntityIDs ]
		relation = kindred.Relation(relationType=relationType,entities=entitiesInRelation,argNames=argNames)
		relations.append(relation)

	combinedData = kindred.Document(text,entities=entities,relations=relations)
	return combinedData

def convertBiocDocToKindredDocs(document):
	assert isinstance(document,bioc.BioCDocument)
	kindredDocs = []
	for passage in document.passages:
		assert isinstance(passage,bioc.BioCPassage)
		
		text = passage.text
		offset = int(native(passage.offset))
		entities = []
		relations = []
		
		for a in passage.annotations:
			assert isinstance(a,bioc.BioCAnnotation)
			
			entityType = a.infons['type']
			sourceEntityID = a.id

			metadata = a.infons
			del metadata['type']
			
			position = []
			segments = []
			
			for l in a.locations:
				assert isinstance(l,bioc.BioCLocation)
				startPos = int(native(l.offset)) - offset
				endPos = startPos + int(native(l.length))

				assert startPos >= 0 and startPos <= len(text) and endPos >= 0 and endPos <= len(text), "Entity offsets (offset=%s,length=%s) are outside the span of the text (%s)" % (str(l.offset),str(l.length),passage.text)

				position.append((startPos,endPos))
				segments.append(text[startPos:endPos])
			
			entityText = " ".join(segments)

			assert entityText == a.text, "Mismatch in entity annotation between expected text (%s) and extracted text (%s) using offset info for passage with text: %s" % (a.text, entityText, text)

			e = kindred.Entity(entityType,entityText,position,sourceEntityID,metadata=metadata)
			entities.append(e)

		sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }
			
		for r in passage.relations:
			assert isinstance(r,bioc.BioCRelation)
			relationType = r.infons['type']
			
			arguments = []
			for n in r.nodes:
				assert isinstance(n,bioc.BioCNode)
				arguments.append((n.role,n.refid))
			arguments = sorted(arguments)
				
			argNames = [ argName for argName,sourceEntityID in arguments]
			sourceEntityIDs = [ sourceEntityID for argName,sourceEntityID in arguments]
			for sourceEntityID in sourceEntityIDs:
				assert sourceEntityID in sourceEntityIDToEntity, "Relation references entity %s which does not exist in BioC document id=%s" % (sourceEntityID,str(document.id))

			entities = [ sourceEntityIDToEntity[sourceEntityID] for sourceEntityID in sourceEntityIDs ]
			
			r = kindred.Relation(relationType,entities,argNames)
			relations.append(r)
		
		metadata = dict(document.infons)
		metadata.update(passage.infons)
		metadata['id'] = document.id
		relData = kindred.Document(text,entities=entities,relations=relations,metadata=metadata)
		kindredDocs.append(relData)

	return kindredDocs

def loadDataFromBioC(filename,ignoreEntities=[]):
	with open(filename, 'r') as fp:
		collection = bioc.load(fp)
	assert isinstance(collection,bioc.BioCCollection)
	
	parsed = []
	for document in collection.documents:
		parsed += convertBiocDocToKindredDocs(document)

	corpus = kindred.Corpus()
	corpus.documents = parsed
	return corpus

def iterLoad(dataFormat,path,corpusSizeCutoff=500):
	"""
	Iteratively load sections of a (presumably large) corpus. This will create a generator that provides kindred.Corpus objects that are subsets of the larger corpus. This should be used to lower the memory requirements (so that the entire file doesn't need to be loaded into memory at one time).

	:param dataFormat: Format of the data files to load (only 'biocxml' is currently supported)
	:param path: Path to data. Can be directory or an individual file (for bioc, json or simpletag)
	:param corpusSizeCutoff: Approximate maximum number of documents to be in each corpus subset
	:type dataFormat: str
	:type path: str
	:type corpusSizeCutoff: int
	:return: Subsets of the BioC file
	:rtype: A kindred.Corpus generator
	"""
	assert dataFormat == 'biocxml'

	corpus = kindred.Corpus()

	if os.path.isdir(path):
		filenames = [ os.path.join(path,x) for x in os.listdir(path) if x.endswith('bioc.xml') ]
	else:
		filenames = [path]

	for filename in filenames:
		with open(filename,'rb') as f:
			parser = bioc.BioCXMLDocumentReader(f)
			for document in parser:
				if len(corpus.documents) >= corpusSizeCutoff:
					yield corpus
					corpus = kindred.Corpus()
				kindredDocs = convertBiocDocToKindredDocs(document)
				for kindredDoc in kindredDocs:
					corpus.addDocument(kindredDoc)

	if len(corpus.documents) > 0:
		yield corpus
	
def load(dataFormat,path,ignoreEntities=[],ignoreComplexRelations=True):
	"""
	Load a corpus from a variety of formats. If path is a directory, it will try to load all files of the corresponding data type. For standoff format, it will use any associated annotations files (with suffixes .ann, .a1 or .a2)
	
	:param dataFormat: Format of the data files to load ('standoff','biocxml','pubannotation','simpletag')
	:param path: Path to data. Can be directory or an individual file. Should be the txt file for standoff.
	:param ignoreEntities: List of entity types to ignore while loading
	:param ignoreComplexRelations: Whether to filter out relations where one argument is another relation (must be True as kindred doesn't currently support complex relations)
	:type dataFormat: str
	:type path: str
	:type ignoreEntities: list
	:type ignoreComplexRelations: bool
	:return: Corpus of loaded documents
	:rtype: kindred.Corpus
	"""
	assert dataFormat in ['standoff','biocxml','pubannotation','simpletag']
	assert ignoreComplexRelations == True, "ignoreComplexRelations must be True as kindred doesn't currently support complex relations"

	corpus = kindred.Corpus()

	if os.path.isdir(path):
		directory = path

		filenames = sorted(list(os.listdir(directory)))

		for filename in filenames:
			if dataFormat == 'standoff' and filename.endswith('.txt'):
				absPath = os.path.join(directory, filename)
				doc = loadDataFromStandoff(absPath,ignoreEntities=ignoreEntities)
				corpus.addDocument(doc)
			elif dataFormat == 'biocxml' and filename.endswith('.bioc.xml'):
				absPath = os.path.join(directory, filename)
				tempCorpus = loadDataFromBioC(absPath,ignoreEntities=ignoreEntities)
				corpus.documents += tempCorpus.documents
			elif dataFormat == 'pubannotation' and filename.endswith('.json'):
				absPath = os.path.join(directory, filename)
				doc = loadDataFromPubAnnotationJSON(absPath,ignoreEntities=ignoreEntities)
				corpus.addDocument(doc)
			elif dataFormat == 'simpletag' and filename.endswith('.simple'):
				absPath = os.path.join(directory, filename)
				with open(absPath,'r') as f:
					filecontents = f.read().strip()

				doc = parseSimpleTag(filecontents,ignoreEntities=ignoreEntities)
				doc.sourceFilename = filename
				corpus.addDocument(doc)

		if len(corpus.documents) == 0:
			raise RuntimeError("No documents loaded from directory (%s). Are you sure this directory contains the corpus (format: %s)" % (path,dataFormat))

	elif dataFormat == 'standoff':
		doc = loadDataFromStandoff(path,ignoreEntities=ignoreEntities)
		corpus.addDocument(doc)
	elif dataFormat == 'biocxml':
		corpus = loadDataFromBioC(path,ignoreEntities=ignoreEntities)
	elif dataFormat == 'pubannotation':
		doc = loadDataFromPubAnnotationJSON(path,ignoreEntities=ignoreEntities)
		corpus.addDocument(doc)
	elif dataFormat == 'simpletag':
		with open(path,'r') as f:
			filecontents = f.read().strip()

		doc = parseSimpleTag(filecontents,ignoreEntities=ignoreEntities)
		doc.sourceFilename = os.path.basename(path)
		corpus.addDocument(doc)

	return corpus
			

