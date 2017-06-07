import kindred


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
