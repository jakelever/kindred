
import kindred
import six

class CandidateRelation:
	"""
	Describes a candidate relation between entities (i.e. one that could exist but has not yet been predicted). Contains information about known relation types and arg names associated with this candidate (from training data) and also a link to the sentence containing this candidate.
	
	:ivar entities: List of entities in relation
	:ivar knownTypesAndArgNames: List of tuples with known relation types and argument names associated with this candidate relation
	:ivar sentence: Parsed sentence containing the candidate relation
	"""
	
	def __init__(self,entities=[],knownTypesAndArgNames=[],sentence=None):
		"""
		Constructor for Candidate Relation class
		
		:param entities: List of entities in relation
		:param knownTypesAndArgNames: List of tuples with known relation types and argument names associated with this candidate relation
		:param sentence: Parsed sentence containing the candidate relation
		:type entities: list of kindred.Entity
		:type knownTypesAndArgNames: list of tuples (str, list of str)
		:type sentence: kindred.Sentence
		"""

		assert isinstance(entities,list),  "entities must be a list of kindred.Entity"
		for entity in entities:
			assert isinstance(entity, kindred.Entity), "entities must be a list of kindred.Entity"
		self.entities = entities

		knownTypesAndArgNamesError = "knownTypesAndArgNames must be a list of tuples where each (length=2) tuple is the name of the relation and a list of argument names"
		assert isinstance(knownTypesAndArgNames,list), knownTypesAndArgNamesError
		for knownTypeAndArgNames in knownTypesAndArgNames:
			assert isinstance(knownTypeAndArgNames, tuple), knownTypesAndArgNamesError
			assert len(knownTypeAndArgNames) == 2, knownTypesAndArgNamesError
			knownType,knownArgNames = knownTypeAndArgNames
			assert isinstance(knownType, six.string_types), knownTypesAndArgNamesError
			assert isinstance(knownArgNames,list), knownTypesAndArgNamesError
			for knownArgName in knownArgNames:
				assert isinstance(knownArgName, six.string_types), knownTypesAndArgNamesError
		self.knownTypesAndArgNames = knownTypesAndArgNames
				
		assert isinstance(sentence, kindred.Sentence)
		self.sentence = sentence
	
	def __eq__(self, other):
		"""Override the default Equals behavior"""
		if isinstance(other, self.__class__):
			return self.__dict__ == other.__dict__
		return False
	
	def __ne__(self, other):
		"""Define a non-equality test"""
		return not self.__eq__(other)

	def __str__(self):
		return "<CandidateRelation %s %s>" % (str(self.entities),str(self.knownTypesAndArgNames))

	def __repr__(self):
		return self.__str__()

	def __hash__(self):
		if self.argNames is None:
			return hash((self.relationType,tuple(self.entities),self.probability,self.sentence))
		else:
			return hash((self.relationType,tuple(self.entities),tuple(self.argNames),self.probability,self.sentence))

