
import sys
import os
import codecs

import kindred

def saveDataFromSTFormat(data,predictedRelations,txtPath,a1Path,a2Path):
	assert isinstance(data,kindred.RelationData)

	with codecs.open(txtPath,'w','utf8') as txtFile, codecs.open(a1Path,'w','utf8') as a1File, codecs.open(a2Path,'w','utf8') as a2File:
		txtFile.write(data.getText())
		
		for e in data.getEntities():
			assert isinstance(e,kindred.Entity)
		
			positions = ";".join("%d %d" % (start,end) for start,end in e.position)
			line = "%s\t%s %s\t%s" % (e.sourceEntityID,e.entityType,positions,e.text)
			a1File.write(line+"\n")
			
		entityIDsToSourceEntityIDs = data.getEntityIDsToSourceEntityIDs()	
		
		for i,r in enumerate(data.getRelations()):
			assert isinstance(r,kindred.Relation)
			
			relationType = r.relationType
			relationEntityIDs = [ entityIDsToSourceEntityIDs[eID] for eID in r.entityIDs ]
			
			if r.argNames is None:
				argNames = [ ("arg%d" % i) for i in range(len(relationEntityIDs)) ]
			else:
				argNames = r.argNames

			arguments = " ".join(["%s:%s" % (a,b) for a,b in zip(argNames,relationEntityIDs) ])
			line = "R%d\t%s %s" % (i,relationType,arguments)
			a2File.write(line+"\n")
			
		for i,r in enumerate(predictedRelations):
			assert isinstance(r,kindred.Relation)
			
			relationType = r.relationType
			inThisText = [ eID in entityIDsToSourceEntityIDs for eID in r.entityIDs ]
			if not all(inThisText):
				# Not all the entities in this relation are in this portion of text. So don't include
				continue
			
			relationEntityIDs = [ entityIDsToSourceEntityIDs[eID] for eID in r.entityIDs ]
			
			if r.argNames is None:
				argNames = [ ("arg%d" % i) for i in range(len(relationEntityIDs)) ]
			else:
				argNames = r.argNames

			arguments = " ".join(["%s:%s" % (a,b) for a,b in zip(argNames,relationEntityIDs) ])
			line = "R%d\t%s %s" % (i,relationType,arguments)
			a2File.write(line+"\n")
			


def save(dataList,dataFormat,directory,predictedRelations=[]):
	assert dataFormat == 'standoff' or dataFormat == 'simpletag' or dataFormat == 'json'

	assert isinstance(dataList,list)
	for d in dataList:
		assert isinstance(d,kindred.RelationData)
	
	for i,d in enumerate(dataList):
		if dataFormat == 'standoff':
			
			if d.getSourceFilename() is None:
				base = "%08d" % i
			else:
				base = d.getSourceFilename()

			txtPath = os.path.join(directory,'%s.txt' % base)
			a1Path = os.path.join(directory,'%s.a1' % base)
			a2Path = os.path.join(directory,'%s.a2' % base)

			saveDataFromSTFormat(d,predictedRelations,txtPath,a1Path,a2Path)

	
