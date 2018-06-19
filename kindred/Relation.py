
import kindred
import six

class Relation:
	"""
	Describes relationship between entities (including relation type and argument names if applicable).
	"""
	
	def __init__(self,relationType=None,entities=[],argNames=None,probability=None):
		"""
		Constructor for Relation class
		
		:param relationType: Type of relation
		:param entities: List of entities in relation
		:param argNames: Names of relation argument associated with each entity
		:param probability: Optional probability for predicted relations
		:type relationType: str
		:type entities: list of kindred.Entity
		:type argNames: list of str
		:type probability: float
		"""

		assert relationType is None or isinstance(relationType, six.string_types), "relationType must be a string"
		self.relationType = relationType

		assert isinstance(entities,list),  "entities must be a list of kindred.Entity"
		for entity in entities:
			assert isinstance(entity, kindred.Entity), "entities must be a list of kindred.Entity"
		self.entities = entities

		if argNames == None:
			self.argNames = None
		else:
			assert len(argNames) == len(entities)
			self.argNames = [ str(a) for a in argNames ]

		if not probability is None:
			assert isinstance(probability, float)
		self.probability = probability
	
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

	def __str__(self):
		return "<Relation %s %s %s>" % (self.relationType,str(self.entities),str(self.argNames))

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		if self.argNames is None:
			return hash((self.relationType,tuple(self.entities),self.probability))
		else:
			return hash((self.relationType,tuple(self.entities),tuple(self.argNames),self.probability))

