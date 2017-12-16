import kindred

def makeTestLookup():
	return {('egfr',):[('gene','HGNC:3236')],('erbb2',):[('gene','HGNC:2064')]}

def test_entityrecognizer_basic():
	lookup = makeTestLookup()

	text = 'EGFR is a gene associated with lung cancer'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'HGNC:3236'
	assert entity.text == 'EGFR'
	assert entity.position == [(0,4)]

def test_entityrecognizer_microRNA_mirOFF():
	lookup = makeTestLookup()

	text = 'mir-83 is a gene associated with lung cancer'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 0

def test_entityrecognizer_microRNA_mir1():
	lookup = makeTestLookup()

	text = 'mir-83 is a gene associated with lung cancer'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectMicroRNA=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'mirna|mir-83'
	assert entity.text == 'mir-83'
	assert entity.position == [(0,6)]

def test_entityrecognizer_microRNA_mir2():
	lookup = makeTestLookup()

	text = 'hsa-mir-83 is a gene associated with lung cancer'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectMicroRNA=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'mirna|mir-83'
	assert entity.text == 'mir-83'
	assert entity.position == [(4,10)]

def test_entityrecognizer_microRNA_mir3():
	lookup = makeTestLookup()

	text = 'microrna-83 is a gene associated with lung cancer'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectMicroRNA=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'mirna|microrna-83'
	assert entity.text == 'microrna-83'
	assert entity.position == [(0,11)]

def test_entityrecognizer_microRNA_mir4():
	lookup = makeTestLookup()

	text = 'mir83 is a gene associated with lung cancer'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectMicroRNA=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'mirna|mir83'
	assert entity.text == 'mir83'
	assert entity.position == [(0,5)]

if __name__ == '__main__':
	test_entityrecognizer_basic()
