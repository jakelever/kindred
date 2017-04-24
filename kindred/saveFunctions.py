
import os
import codecs

import kindred

def saveDataFromSTFormat(data,txtPath,a1Path,a2Path):
	assert isinstance(data,kindred.RelationData)

	with codecs.open(txtPath,'w','utf8') as txtFile, open(a1Path,'w') as a1File, open(a2Path,'w') as a2File:
		txtFile.write(data.getText())
		for e in data.getEntities():
			positions = " ".join("%d %d" % (start,end) for start,end in e.entityLocs)
			line = "%s\t%s %s %s" % (e.sourceEntityID,e.entityType,positions,e.text)
			a1File.write(line+"\n")
		for i,r in enumerate(data.getRelations()):
			relationType = r.relationType
			relationEntityIDs = r.entitiesInRelation

			if r.argNames in None:
				argNames = [ "arg%d" for i in range(len(relationEntityIDs)) ]
			else:
				argNames = r.argNames

			arguments = " ".join(["%s:%s" % (a,b) for a,b in zip(relationEntityIDs,argNames) ])
			line = "R%d\t%s %s" % (i,relationType,arguments)


def save(dataList,dataFormat,directory):
	assert dataFormat == 'standoff' or dataFormat == 'simpletag' or dataFormat == 'json'

	assert isinstance(dataList,list)
	for d in dataList:
		assert isinstance(d,kindred.RelationData)
	
	for i,d in enumerate(dataList):
		if dataFormat == 'standoff':
			
			if d.getSourceFilename() is None:
				base = "08%d" % i
			else:
				base = d.getSourceFilename()

			txtPath = os.path.join(directory,'%s.txt' % base)
			a1Path = os.path.join(directory,'%s.a1' % base)
			a2Path = os.path.join(directory,'%s.a2' % base)

			saveDataFromSTFormat(d,txtPath,a1Path,a2Path)

	
