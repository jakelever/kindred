
import xml.etree.ElementTree
import sys

import kindred
from kindred import CandidateBuilder

from kindred.loadFunctions import loadDoc,loadDocs,loadDir
from kindred.saveFunctions import save
from kindred.evalFunctions import evaluate
from kindred import bionlpst, pubannotation, pubtator
from kindred.Dependencies import downloadCoreNLP

class Entity:
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
		out = "%s:'%s' id=%d sourceid=%s %s" % (self.entityType,self.text,self.entityID,str(self.sourceEntityID),str(self.position))
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

class TextAndEntityData_UNUSED:
	def __init__(self,text,sourceFilename=None,entities=None):
		self.sourceFilename = sourceFilename

		if entities is None:
			#self.text,self.entities = self.processTaggedText(text)
			relationDataWithoutRelations = kindred.loadFunctions.parseSimpleTag(text)
			assert len(relationDataWithoutRelations.getRelations()) == 0, "Cannot load simple tagged text into TextAndEntityData with relations"
			
			self.text = relationDataWithoutRelations.getText()
			self.entities = relationDataWithoutRelations.getEntities()
		else:
			assert isinstance(entities,list)
			for e in entities:
				assert isinstance(e,Entity)

			self.text = text
			self.entities = entities
		
	def getEntities(self):
		return self.entities
		
	def getSourceEntityIDsToEntityIDs(self):
		return {e.sourceEntityID:e.entityID for e in self.entities}
	
	def getEntityIDsToSourceEntityIDs(self):
		return {e.entityID:e.sourceEntityID for e in self.entities}
		
	def getEntityIDsToEntityTypes(self):
		return {e.entityID:e.entityType for e in self.entities}
	
	def getEntityIDsToEntities(self):
		return {e.entityID:e for e in self.entities}
	
	def getEntityIDs(self):
		return [e.entityID for e in self.entities]

	def getSourceFilename(self):
		return self.sourceFilename
		
	def getText(self):
		return self.text
		
	def __str__(self):
		return str((self.text,self.entities.__str__()))
		
	def __repr__(self):
		return self.__str__()
		
class Corpus:
	def __init__(self,text=None):
		self.documents = []
		if not text is None:
			doc = kindred.Document(text)
			self.addDocument(doc)

	def addDocument(self,doc):
		assert isinstance(doc,kindred.Document)
		self.documents.append(doc)

	def clone(self):
		cloned = Corpus()
		for doc in self.documents:
			cloned.addDocument(doc.clone())
		return cloned

	def getRelations(self):
		relations = []
		for doc in self.documents:
			relations += doc.getRelations()
		return relations

	def removeRelations(self):
		for doc in self.documents:
			doc.removeRelations()

class Document:
	def __init__(self,text,entities=None,relations=None,relationsUseSourceIDs=True,sourceFilename=None):
		loadFromSimpleTag = (entities is None)

		self.sourceFilename = sourceFilename

		if loadFromSimpleTag:
			dataToCopy = kindred.loadFunctions.parseSimpleTag(text)
			self.text = dataToCopy.getText()
			self.entities = dataToCopy.getEntities()
			self.relations = dataToCopy.getRelations()
		else:
			self.text = text
			
			assert isinstance(entities,list)
			for e in entities:
				assert isinstance(e,Entity)
			self.entities = entities
			
			if relations is None:
				self.relations = []
			else:
				assert isinstance(relations,list)
				for r in relations:
					assert isinstance(r,Relation)
				self.relations = relations

		# We'll need to translate source IDs to internal IDs
		if relationsUseSourceIDs and not loadFromSimpleTag:
			sourceEntityIDsToEntityIDs = self.getSourceEntityIDsToEntityIDs()
			sourceEntityIDs = sourceEntityIDsToEntityIDs.keys()
			correctedRelations = []
			for r in self.relations:
				for e in r.entityIDs:
					assert e in sourceEntityIDs, "Entities in relation must occur in the associated text. %s does not" % e
				relationEntityIDs = [ sourceEntityIDsToEntityIDs[e] for e in r.entityIDs ]
				correctedR = Relation(r.relationType,relationEntityIDs,r.argNames)
				correctedRelations.append(correctedR)
				
			self.relations = correctedRelations

		self.processedSentences = []

	def clone(self):
		cloned = Document(self.text,entities=self.entities,relations=self.relations,relationsUseSourceIDs=False,sourceFilename=self.sourceFilename)
		return cloned

	def removeRelations(self):
		self.relations = []

	def addProcessedSentence(self,sentence):
		assert isinstance(sentence,kindred.ProcessedSentence)
		self.processedSentences.append(sentence)
	
	def addRelation(self,relation):
		self.relations.append(relation)

	def getEntities(self):
		return self.entities
		
	def getText(self):
		return self.text
		
	def getRelations(self):
		return self.relations
	
	def getSourceEntityIDsToEntityIDs(self):
		return {e.sourceEntityID:e.entityID for e in self.entities}
	
	def getEntityIDsToSourceEntityIDs(self):
		return {e.entityID:e.sourceEntityID for e in self.entities}
		
	def getEntityIDsToEntityTypes(self):
		return {e.entityID:e.entityType for e in self.entities}
	
	def getEntityIDsToEntities(self):
		return {e.entityID:e for e in self.entities}
	
	def getEntityIDs(self):
		return [e.entityID for e in self.entities]

	def getSourceFilename(self):
		return self.sourceFilename

	def __str__(self):
		return str((self.textAndEntityData.__str__(),self.relations))
		
	def __repr__(self):
		return self.__str__()
	
class CandidateRelation:
	def __init__(self,processedSentence,entitiesInRelation):
		assert isinstance(processedSentence,ProcessedSentence)
		assert isinstance(entitiesInRelation,tuple)
		assert len(entitiesInRelation) > 1
		
		entitiesInSentence = processedSentence.getEntityIDs()
		
		for entityID in entitiesInRelation:
			assert entityID in entitiesInSentence, "All entities in candidate relation should actually be in the associated sentence"
			
		self.processedSentence = processedSentence
		self.entitiesInRelation = entitiesInRelation
		
	def getEntityTypes(self):
		return [ self.processedSentence.getEntityType(eID) for eID in self.entitiesInRelation]

		
	def __str__(self):
		return str((self.processedSentence.__str__(),self.entitiesInRelation))
		
	def __repr__(self):
		return self.__str__()
		
	
class Token:
	def __init__(self,word,lemma,partofspeech,startPos,endPos):
		self.word = word
		self.lemma = lemma
		self.partofspeech = partofspeech
		self.startPos = startPos
		self.endPos = endPos

	def __str__(self):
		return self.word
		
	def __repr__(self):
		return self.__str__()

class ProcessedEntity:
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

class ProcessedSentence:
	# TODO: Camelcase consistency in this class

	def __str__(self):
		tokenWords = [ t.word for t in self.tokens ]
		return " ".join(tokenWords)

	def getEntityIDs(self):
		return [ e.entityID for e in self.processedEntities ]
		
	def getEntityType(self,entityID):
		return self.entityIDToType[entityID]

	def __init__(self, tokens, dependencies, processedEntities, sourceFilename=None):
		assert isinstance(tokens, list) 
		assert isinstance(dependencies, list) 
		assert isinstance(processedEntities, list)
		for e in processedEntities:
			assert isinstance(e,ProcessedEntity)
		
		self.tokens = tokens
		self.processedEntities = processedEntities
		self.sourceFilename = sourceFilename
		
		self.dependencies = dependencies
		
		self.entityIDToType = { e.entityID:e.entityType for e in self.processedEntities }
	

