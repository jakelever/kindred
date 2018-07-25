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

def loadEntity(line,text):
	assert line[0] == 'T', "Entity input should start with a T"
	split = line.strip().split('\t')
	assert len(split) == 3
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

	assert chunkTest == tokensTest , u"For id=" + entityID + ", tokens '" + tokens.encode('ascii', 'ignore') + "' don't match up with positions: " + str(positions)
	
	entity = kindred.Entity(typeName, tokensTest, positions, entityID)

	return entity
	
def loadRelation(line,ignoreComplexRelations=True):
	assert line[0] == 'E' or line[0] == 'R', "Relation input should start with a E or R"
	assert ignoreComplexRelations == True, "ignoreComplexRelations must be True as kindred doesn't currently support complex relations"

	split = line.strip().split('\t')
	eventInfo = split[1]
	typeSpacePos = eventInfo.index(' ')
	
	eventNameSplit = eventInfo[:typeSpacePos].split(':')
	assert len(eventNameSplit) == 1, "Cannot load trigger events"
	relationType = eventNameSplit[0]
		
	isComplexRelation = False
	argumentText = eventInfo[typeSpacePos:]
	arguments = []
	for argument in argumentText.strip().split(' '):
		split2 = argument.strip().split(':')
		assert len(split2) == 2
		tmpArgName = split2[0]
		tmpEntityID = split2[1]

		isComplexRelation = (tmpEntityID[0] == 'R' or tmpEntityID[0] == 'E')

		# We'll skip this relation as
		if ignoreComplexRelations and isComplexRelation:
			break

		assert not isComplexRelation, "kindred does not support complex relations (where one relation has another relation as an argument), use ignoreComplexRelations=True to ignore these"

		assert not tmpArgName in arguments
		arguments.append((tmpArgName,tmpEntityID))

	if ignoreComplexRelations and isComplexRelation:
		return None

	arguments = sorted(arguments)
	sourceEntityIDs = [ entityID for argName,entityID in arguments ]
	argNames = [ argName for argName,entityID in arguments ]

	relationTuple = (relationType,sourceEntityIDs,argNames)
	return relationTuple
	
# TODO: Deal with complex relations more clearly
def loadDataFromSTFormat(txtFile,a1File,a2File,verbose=False,ignoreEntities=[],ignoreComplexRelations=True):
	assert ignoreComplexRelations == True, "ignoreComplexRelations must be True as kindred doesn't currently support complex relations"

	with codecs.open(txtFile, "r", "utf-8") as f:
		text = f.read()
			
	entities = []
	with codecs.open(a1File, "r", "utf-8") as f:
		for line in f:
			if line.strip() == '':
				continue
				
			assert line[0] == 'T', "Only triggers are expected in a1 file: " + a1File
			entity = loadEntity(line.strip(), text)
			if (not entity is None) and (not entity.entityType in ignoreEntities):
				entities.append(entity)
		
	sourceEntityIDToEntity = { entity.sourceEntityID:entity for entity in entities }

	relations = []
	if os.path.exists(a2File):
		with codecs.open(a2File, "r", "utf-8") as f:
			for line in f:
				if line.strip() == '':
					continue
					
				if line[0] == 'E' or line[0] == 'R':
					relationTuple = loadRelation(line.strip(),ignoreComplexRelations)
					if not relationTuple is None:
						relationType,sourceEntityIDs,argNames = relationTuple
						entitiesInRelation = [ sourceEntityIDToEntity[sourceEntityID] for sourceEntityID in sourceEntityIDs ]
						relation = kindred.Relation(relationType,entitiesInRelation,argNames)
						relations.append(relation)
				elif verbose:
					sys.stderr.write("Unable to process line: %s\n" % line.strip())
	elif verbose:
		sys.stderr.write("Note: No A2 file found : %s\n" % os.path.basename(a2File))

	baseTxtFile = os.path.basename(txtFile)
	baseFilename = baseTxtFile[0:-4]

	combinedData = kindred.Document(text,entities=entities,relations=relations,sourceFilename=baseFilename)
			
	return combinedData

def parseJSON(data,ignoreEntities=[]):
	entities = []
	relations = []

	if isinstance(data,list):
		assert len(data) == 1 and isinstance(data[0],dict), "JSON loading expects a dictionary or a list with one dictionary in it"
		data = data[0]
	assert isinstance(data,dict), "JSON loading expects a dictionary or a list with one dictionary in it"

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
			obj = r['obj']
			relationType = r['pred']
			subj = r['subj']
			
			sourceEntityIDs = [obj,subj]
			argNames = ['obj','subj']
			entitiesInRelation = [ sourceEntityIDToEntity[sourceEntityID] for sourceEntityID in sourceEntityIDs ]
		
			relation = kindred.Relation(relationType,entitiesInRelation,argNames)
			relations.append(relation)
	
	expected = ['denotations','divid','modifications','namespaces','project','relations','sourcedb','sourceid','target','text','tracks']
	extraFields = [ k for k in data.keys() if not k in expected]
	assert len(extraFields) == 0, "Found additional unexpected fields (%s) in JSON" % (",".join(extraFields))
		
	combinedData = kindred.Document(text,entities=entities,relations=relations)

	return combinedData

def loadDataFromJSON(filename,ignoreEntities=[]):
	with open(filename) as f:
		data = json.load(f)
	parsed = parseJSON(data,ignoreEntities)
	
	baseTxtFile = os.path.basename(filename)
	parsed.sourceFilename = baseTxtFile
	
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
			
			position = []
			segments = []
			
			for l in a.locations:
				assert isinstance(l,bioc.BioCLocation)
				startPos = int(native(l.offset)) - offset
				endPos = startPos + int(native(l.length))
				position.append((startPos,endPos))
				segments.append(text[startPos:endPos])
			
			entityText = " ".join(segments)
			e = kindred.Entity(entityType,entityText,position,sourceEntityID)
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
				
			sourceEntityIDs = [ entityID for argName,entityID in arguments]
			argNames = [ argName for argName,entityID in arguments]
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
	return parsed

def iterLoadDataFromBioc(filename,corpusSizeCutoff=500):
	"""
	Iteratively load documents from a BioC file. This will a generator that provides kindred.Corpus objects that are subsets of the entire BioC file. This should be used to lower the memory requirements (so that the entire file doesn't need to be loaded into memory at one time).

	:param filename: Path of the Bioc file
	:param corpusSizeCutoff: Approximate maximum number of documents to be in each corpus subset
	:type filename: str
	:type corpusSizeCutoff: int
	:return: Subsets of the BioC file
	:rtype: A kindred.Corpus generator
	"""
	corpus = kindred.Corpus()
	with bioc.iterparse(filename) as parser:
		for document in parser:
			if len(corpus.documents) >= corpusSizeCutoff:
				yield corpus
				corpus = kindred.Corpus()
			kindredDocs = convertBiocDocToKindredDocs(document)
			for kindredDoc in kindredDocs:
				corpus.addDocument(kindredDoc)

	if len(corpus.documents) > 0:
		yield corpus
	
	
def loadDoc(dataFormat,path=None,txtPath=None,a1Path=None,a2Path=None,verbose=False,ignoreEntities=[],ignoreComplexRelations=True):
	"""
	Loads a single document from a single file (for JSON or SimpleTag) or set of files (for standoff)

	:param dataFormat: The format of the data to load (standoff/simpletag/json)
	:param path: Path of the file (for simpletag/json)
	:param txtPath: Path of the TXT file (for standoff)
	:param a1Path: Path of the A1 file (for standoff)
	:param a2Path: Path of the A2 file (for standoff)
	:param verbose: Whether to give additional output while loading
	:param ignoreEntities: A list of entities to ignore while loading
	:param ignoreComplexRelations: Whether to ignore complex relations (relations where one argument is another relations). This must be true as kindred doesn't currently support complex relations
	:type dataFormat: str
	:type path: str
	:type txtPath: str
	:type a1Path: str
	:type a2Path: str
	:type verbose: bool
	:type ignoreEntities: list of str
	:type ignoreComplexRelations: bool
	:return: Loaded document
	:rtype: kindred.Document
	"""
	
	assert dataFormat == 'standoff' or dataFormat == 'simpletag' or dataFormat == 'json'
	assert ignoreComplexRelations == True, "ignoreComplexRelations must be True as kindred doesn't currently support complex relations"
	
	if dataFormat == 'standoff':
		assert not txtPath is None
		assert not a1Path is None

		doc = loadDataFromSTFormat(txtPath,a1Path,a2Path,verbose=verbose,ignoreEntities=ignoreEntities)
	elif dataFormat == 'simpletag':
		assert not path is None

		with open(path,'r') as f:
			filecontents = f.read().strip()
		doc = parseSimpleTag(filecontents,ignoreEntities=ignoreEntities)
		doc.sourceFilename = os.path.basename(path)
	elif dataFormat == 'json':
		assert not path is None
		doc = loadDataFromJSON(path,ignoreEntities=ignoreEntities)

	assert isinstance(doc,kindred.Document)
	return doc

def loadDocs(dataFormat,path=None,ignoreEntities=[]):
	"""
	Load multiple documents from a single file (currently only BioC)

	:param dataFormat: The format of the data to load (bioc)
	:param path: Path of the file
	:param ignoreEntities: A list of entities to ignore while loading
	:type dataFormat: str
	:type path: str
	:type ignoreEntities: list of str
	:return: Loaded documents
	:rtype: list of kindred.Document
	"""
	assert dataFormat == 'bioc'

	if dataFormat == 'bioc':
		assert not path is None
		docs = loadDataFromBioC(path,ignoreEntities=ignoreEntities)
		
	assert isinstance(docs,list)
	for doc in docs:
		assert isinstance(doc,kindred.Document)
		
	return docs
	
def loadDir(dataFormat,directory,verbose=False,ignoreEntities=[],ignoreComplexRelations=True):
	"""
	Load a directory of corpus data from a variety of data formats
	
	:param dataFormat: Format of the data files to load ('standoff','simpletag','json' or 'bioc')
	:param directory: Path to directory of data to load
	:param verbose: Whether to print statements about loading to std out
	:param ignoreEntities: List of entity types to ignore while loading
	:param ignoreComplexRelations: Whether to filter out relations where one argument is another relation (must be True as kindred doesn't currently support complex relations)
	:type dataFormat: str
	:type directory: str
	:type verbose: bool
	:type ignoreEntities: list
	:type ignoreComplexRelations: bool
	:return: Corpus of loaded documents
	:rtype: kindred.Corpus
	"""
	assert dataFormat == 'standoff' or dataFormat == 'simpletag' or dataFormat == 'json' or dataFormat == 'bioc'
	assert os.path.isdir(directory), "%s must be a directory"
	assert ignoreComplexRelations == True, "ignoreComplexRelations must be True as kindred doesn't currently support complex relations"
	
	if directory[-1] != '/':
		directory += '/'

	filenames = sorted(list(os.listdir(directory)))

	corpus = kindred.Corpus()
	for filename in filenames:
		if dataFormat == 'standoff' and filename.endswith('.txt'):
			base = filename[0:-4]
			txtPath = os.path.join(directory, base + '.txt')
			a1Path = os.path.join(directory, base + '.a1')
			a2Path = os.path.join(directory, base + '.a2')

			assert os.path.isfile(txtPath), "%s must exist" % txtPath
			assert os.path.isfile(a1Path), "%s must exist" % a1Path

			doc = loadDoc(dataFormat,txtPath=txtPath,a1Path=a1Path,a2Path=a2Path,verbose=verbose,ignoreEntities=ignoreEntities,ignoreComplexRelations=ignoreComplexRelations)
			corpus.addDocument(doc)
		elif dataFormat == 'simpletag' and filename.endswith('.simple'):
			absPath = os.path.join(directory, filename)
			doc = loadDoc(dataFormat,path=absPath,verbose=verbose,ignoreEntities=ignoreEntities,ignoreComplexRelations=ignoreComplexRelations)
			corpus.addDocument(doc)
		elif dataFormat == 'json' and filename.endswith('.json'):
			absPath = os.path.join(directory, filename)
			doc = loadDoc(dataFormat,path=absPath,verbose=verbose,ignoreEntities=ignoreEntities,ignoreComplexRelations=ignoreComplexRelations)
			corpus.addDocument(doc)
		elif dataFormat == 'bioc' and filename.endswith('.bioc.xml'):
			absPath = os.path.join(directory, filename)
			docs = loadDocs(dataFormat,path=absPath,ignoreEntities=ignoreEntities)
			for doc in docs:
				corpus.addDocument(doc)
	
	if len(corpus.documents) == 0:
		raise RuntimeError("No documents loaded from directory (%s). Are you sure this directory contains the corpus (format: %s)" % (directory,dataFormat))

	return corpus
			
			
