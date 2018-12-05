
class Token:
	"""
	Individual word with lemma, part-of-speech and location in text.
	
	:ivar word: Unprocessed word
	:ivar lemma: Lemmatized word
	:ivar partofspeech: Part-of-speech of word
	:ivar startPos: Start position of token in sentence
	:ivar endPos: End position of token in sentence
	"""
	
	def __init__(self,word,lemma,partofspeech,startPos,endPos):
		"""
		Constructor for Token class
		
		:param word: Unprocessed word
		:param lemma: Lemmatized word
		:param partofspeech: Part-of-speech of word
		:param startPos: Start position of token in sentence
		:param endPos: End position of token in sentence
		:type word: str
		:type lemma: str
		:type partofspeech: str
		:type startPos: int
		:type endPos: int
		"""

		self.word = word
		self.lemma = lemma
		self.partofspeech = partofspeech
		self.startPos = startPos
		self.endPos = endPos

	def __str__(self):
		return self.word
		
	def __repr__(self):
		return self.__str__()
