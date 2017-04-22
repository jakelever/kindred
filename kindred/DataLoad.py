import codecs
import os
import json
from pprint import pprint
import sys
import re

import kindred

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

	#print chunkTest, '|', tokensTest
	assert chunkTest == tokensTest , u"For id=" + entityID + ", tokens '" + tokens.encode('ascii', 'ignore') + "' don't match up with positions: " + str(positions)
	
	entity = kindred.Entity(typeName, tokensTest, positions, entityID)

	if typeName == 'Title' or typeName == 'Paragraph':
		return None

	return entity
	
def loadRelation(line,ignoreComplexRelations=False):
	assert line[0] == 'E' or line[0] == 'R', "Relation input should start with a E or R"
	split = line.strip().split('\t')
	relationID = split[0]
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
		argName = split2[0]
		entityID = split2[1]

		isComplexRelation = (entityID[0] == 'R' or entityID[0] == 'E')

		# We'll skip this relation as
		if ignoreComplexRelations and isComplexRelation:
			break

		assert not isComplexRelation, "kindred does not support complex relations (where one relation has another relation as an argument), use ignoreComplexRelations=True to ignore these"

		assert not argName in arguments
		arguments.append((argName,entityID))

	if ignoreComplexRelations and isComplexRelation:
		return None

	arguments = sorted(arguments)
	entityIDs = [ entityID for argName,entityID in arguments ]
	argNames = [ argName for argName,entityID in arguments ]

	relation = kindred.Relation(relationType, entityIDs, argNames)
	return relation
	
def loadDataFromSTFormat(txtFile,a1File,a2File,verbose=False,ignoreComplexRelations=False):
	with codecs.open(txtFile, "r", "utf-8") as f:
		text = f.read()
			
	entities = []
	with codecs.open(a1File, "r", "utf-8") as f:
		for line in f:			
			assert line[0] == 'T', "Only triggers are expected in a1 file: " + a1File
			entity = loadEntity(line.strip(), text)
			if not entity is None:
				entities.append(entity)
			
	relations = []
	if os.path.exists(a2File):
		with codecs.open(a2File, "r", "utf-8") as f:
			for line in f:
				if line[0] == 'E' or line[0] == 'R':
					relation = loadRelation(line.strip(),ignoreComplexRelations)
					if not relation is None:
						relations.append(relation)
				elif verbose:
					print "Unable to process line: %s" % line.strip()
	else:
		print "Note: No A2 file found. ", a2File

	baseTxtFile = os.path.basename(txtFile)
	combinedData = kindred.RelationData(text,relations,entities=entities,sourceFilename=baseTxtFile)
			
	return combinedData

def loadDataFromSTFormat_Directory(directory,verbose=False,ignoreComplexRelations=False):
	assert os.path.isdir(directory), "%s must be a directory"
	
	if directory[-1] != '/':
		directory += '/'

	allData = []
	for filename in os.listdir(directory):
		if filename.endswith('.txt'):
			base = filename[0:-4]
			txtFilename = directory + base + '.txt'
			a1Filename = directory + base + '.a1'
			a2Filename = directory + base + '.a2'

			assert os.path.isfile(txtFilename), "%s must exist" % txtFilename
			assert os.path.isfile(a1Filename), "%s must exist" % a1Filename

			data = loadDataFromSTFormat(txtFilename,a1Filename,a2Filename,verbose,ignoreComplexRelations)
			allData.append(data)
	return allData
	
def loadDataFromJSON(filename):
	denotations = {}
	relations = []
	modifications = {}
	
	with open(filename) as f:
		data = json.load(f)
		text = data['text']
		if 'denotations' in data:
			for d in data['denotations']:
				id = d['id']
				type = d['obj']
				span = d['span']
				start,end = span['begin'],span['end']
				denotation = (type,[(start,end)],None)
				denotations[id] = denotation
		if 'relations' in data:
			for r in data['relations']:
				id = r['id']
				obj = r['obj']
				pred = r['pred']
				subj = r['subj']
				relation = ((pred,),obj,subj)
				relations.append(relation)
		if 'modifications' in data:
			for m in data['modifications']:
				id = m['id']
				obj = m['obj']
				pred = m['pred']
				modification = (pred,obj)
				modifications[id] = modification

		expected = ['denotations','divid','modifications','namespaces','project','relations','sourcedb','sourceid','target','text']
		extraFields = [ k for k in data.keys() if not k in expected]
		assert len(extraFields) == 0, "Found additional unexpected fields (%s) in JSON FILE : %s" % (",".join(extraFields), filename)

	return text,denotations,relations,modifications

