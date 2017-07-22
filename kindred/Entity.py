import kindred
import sys

class Entity:
	"""
	Biomedical entity with information of location in text
	"""
	
	nextInternalID = 1

	def __init__(self,entityType,text,position,sourceEntityID=None):
		posErrorMsg = "Entity position must be list of tuples (startPos,endPos)"

		if sys.version_info >= (3, 0):
			assert isinstance(entityType,str)
			assert isinstance(text,str)
		else:
			assert isinstance(entityType,basestring) or isinstance(entityType,unicode)
			assert isinstance(text,basestring) or isinstance(text,unicode)

		assert isinstance(position,list), posErrorMsg
		for p in position:
			assert isinstance(p,tuple), posErrorMsg
			assert len(p) == 2, posErrorMsg
			assert isinstance(p[0],int), posErrorMsg
			assert isinstance(p[1],int), posErrorMsg
	
		self.entityType = entityType
		self.sourceEntityID = sourceEntityID
		self.text = text
		self.position = position
		
		self.entityID = Entity.nextInternalID
		Entity.nextInternalID += 1
		
	def __str__(self):
		out = "<Entity %s:'%s' id=%d sourceid=%s %s>" % (self.entityType,self.text,self.entityID,str(self.sourceEntityID),str(self.position))
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

