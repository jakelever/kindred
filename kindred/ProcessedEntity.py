import kindred


class ProcessedEntity:
	"""
	Entity associated with tokenized text
	"""
	
	def __init__(self,entityType,entityLocs,entityID,sourceEntityID,entityPosition,entityText):
		self.entityType = entityType
		self.entityLocs = entityLocs
		self.entityID = entityID
		self.sourceEntityID = sourceEntityID
		self.entityPosition = entityPosition
		self.entityText = entityText

	def __str__(self):
		return "[ProcessedEntity %s %s %s %s]" % (self.entityType,str(self.entityLocs),str(self.entityID),str(self.sourceEntityID))

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

