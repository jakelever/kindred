import kindred

def test_entityrecognizer_basic():
	lookup = {('egfr',):[('gene','HGNC:3236')],('erbb2',):[('gene','HGNC:2064')]}
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

if __name__ == '__main__':
	test_entityrecognizer_basic()
