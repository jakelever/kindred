import six

class Entity:
	"""
	Biomedical entity with information of location in text

	:ivar entityType: Type of the entity
	:ivar text: Text of the entity
	:ivar position: Position within the text passage at which point entity appears. Entity may be non-contigious
	:ivar sourceEntityID: Entity ID used in source document
	:ivar externalID: ID associated with external ontology (e.g. Hugo Gene ID)
	"""
	
	_nextInternalID = 1

	def __init__(self,entityType,text,position,sourceEntityID=None,externalID=None):
		"""
		Constructor for Entity class
		
		:param entityType: Type of the entity
		:param text: Text of the entity
		:param position: Position within the text passage at which point entity appears. Entity may be non-contigious
		:param sourceEntityID: Entity ID used in source document
		:param externalID: ID associated with external ontology (e.g. Hugo Gene ID)
		:type entityType: str
		:type text: str
		:type position: list of tuples of two integers
		:type sourceEntityID: str
		:type externalID: str
		"""
	
		assert isinstance(entityType, six.string_types), "entityType must be a string"
		assert isinstance(text, six.string_types), "text must be a string"
		assert externalID is None or isinstance(externalID, six.string_types), "externalID must be a string or None"

		posErrorMsg = "Entity position must be list of tuples (startPos,endPos)"
		assert isinstance(position,list), posErrorMsg
		for p in position:
			assert isinstance(p,tuple), posErrorMsg
			assert len(p) == 2, posErrorMsg
			assert isinstance(p[0],int), posErrorMsg
			assert isinstance(p[1],int), posErrorMsg
	
		self.entityType = entityType
		self.sourceEntityID = sourceEntityID
		self.externalID = externalID
		self.text = text
		self.position = position
		
		self.entityID = Entity._nextInternalID
		Entity._nextInternalID += 1
		
	def __str__(self):
		if self.externalID is None:
			out = "<Entity %s:'%s' id=%d sourceid=%s %s>" % (self.entityType,self.text,self.entityID,str(self.sourceEntityID),str(self.position))
		else:
			out = "<Entity %s:'%s' id=%d sourceid=%s externalid=%s %s>" % (self.entityType,self.text,self.entityID,str(self.sourceEntityID),str(self.externalID),str(self.position))
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

	def __hash__(self):
		return hash((self.entityType,self.text,tuple(self.position),self.sourceEntityID,self.externalID))
