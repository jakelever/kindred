
class Relation:
	"""
	Describes relationship between entities (including relation type and argument names if applicable).
	"""
	
	def __init__(self,relationType=None,entityIDs=[],argNames=None):
		"""
		Constructor for Relation class
		
		:param relationType: Type of relation
		:param entityIDs: List of entities in relation
		:param argNames: Names of relation argument associated with each entity
		:type relationType: str
		:type entityIDs: list of ints
		:type argNames: list of str
		"""

		assert isinstance(entityIDs,list)

		self.relationType = relationType
		self.entityIDs = entityIDs
		if argNames == None:
			self.argNames = None
		else:
			assert len(argNames) == len(entityIDs)
			self.argNames = [ str(a) for a in argNames ]
	
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

	def __str__(self):
		return "<Relation %s %s %s>" % (self.relationType,str(self.entityIDs),str(self.argNames))

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		if self.argNames is None:
			return hash((self.relationType,tuple(self.entityIDs)))
		else:
			return hash((self.relationType,tuple(self.entityIDs),tuple(self.argNames)))
