import kindred


class Relation:
	def __init__(self,relationType,entityIDs,argNames=None):
		assert isinstance(entityIDs,list)

		self.relationType = relationType
		self.entityIDs = entityIDs
		self.argNames = argNames
	
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

	def __str__(self):
		return "[Relation %s %s %s]" % (self.relationType,str(self.entityIDs),str(self.argNames))

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		if self.argNames is None:
			return hash((self.relationType,tuple(self.entityIDs)))
		else:
			return hash((self.relationType,tuple(self.entityIDs),tuple(self.argNames)))
