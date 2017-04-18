
from kindred import *
import xml.etree.ElementTree
import sys

class Entity:
	def __init__(self,entityType,entityID,text,start,end):
		self.entityType = entityType
		self.entityID = entityID
		self.text = text
		self.start = start
		self.end = end
		
	def __str__(self):
		out = "%s:'%s' id=%d (%d:%d)" % (self.entityType,self.text,self.entityID,self.start,self.end)
		return out
		
	def __repr__(self):
		return self.__str__()
		
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)


class TextAndEntityData:
	def __init__(self,text):
		#doc = "<doc>%s</doc>" % text
		#e = xml.etree.ElementTree.fromstring(doc)
		#for child in e:
		#	print child, child.text
		#for child in e.itertext():
		#	print child,type(child)
		#print(dir(e))
		#print e, e.text
		text = text.replace('>','<')
		split = text.split('<')
		
		#usingPredefinedIDs = False
		isTag = False
		currentText = ""
		openTags = {}
		minID = 1
		entities = []
		for section in split:
			if isTag:
				tagSplit = section.split(' ')
				assert len(tagSplit) == 1 or len(tagSplit) == 2
				if len(tagSplit) == 1:
					if section.startswith('/'): # close a tag
						entityType = section[1:]
						if entityType in openTags:
							entityStart,entityID = openTags[entityType]
							entityEnd = len(currentText)
							entityText = currentText[entityStart:]
							entity = Entity(entityType,entityID,entityText,entityStart,entityEnd)
							entities.append(entity)
							del openTags[entityType]
					else: # open a tag
						entityType = section
						openTags[entityType] = (len(currentText),minID)
						minID += 1
				elif len(tagSplit) == 2:
					entityType,idinfo = tagSplit
					assert idinfo.startswith('id=')
					idinfoSplit = idinfo.split('=')
					assert len(idinfoSplit) == 2
					entityid = int(idinfoSplit[1])
					assert False
			else:
				currentText += section
				
			# Flip each iteration
			isTag = not isTag
			
		assert len(openTags) == 0, "All tags were not closed in %s" % text
		
		self.text = currentText
		self.entities = entities
		
	def getEntities(self):
		return self.entities
		
	def getText(self):
		return self.text
		
		