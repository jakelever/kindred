import kindred

def makeTestLookup():
	lookup = {}
	lookup[('egfr',)] = [('gene','HGNC:3236')]
	lookup[('erbb2',)] = [('gene','HGNC:2064')]
	lookup[('fgfr3',)] = [('gene','HGNC:3690')]
	lookup[('tacc3',)] = [('gene','HGNC:11524')]
	lookup[('her2',)] = [('gene','HGNC:2064')]
	lookup[('neu',)] = [('gene','HGNC:2064')]
	#DOID:3908       non-small cell lung carcinoma
	lookup[('non','-','small','cell','lung','carcinoma')] = [('cancer','DOID:3908')]
	lookup[('nsclc',)] = [('cancer','DOID:3908')]

	return lookup

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

def test_entityrecognizer_fusion_OFF():
	lookup = makeTestLookup()

	text = 'EGFR-ERBB2 is not a real fusion gene'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 2
	entity1,entity2 = doc.entities
	
	assert entity1.entityType == 'gene'
	assert entity1.externalID == 'HGNC:3236'
	assert entity1.text == 'EGFR'
	assert entity1.position == [(0,4)]

	assert entity2.entityType == 'gene'
	assert entity2.externalID == 'HGNC:2064'
	assert entity2.text == 'ERBB2'
	assert entity2.position == [(5,10)]

def test_entityrecognizer_fusion_1():
	lookup = makeTestLookup()

	text = 'EGFR-ERBB2 is not a real fusion gene, but FGFR3-TACC3 is.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectFusionGenes=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 2
	entity1,entity2 = doc.entities
	
	assert entity1.entityType == 'gene'
	assert entity1.externalID == 'combo|HGNC:3236|HGNC:2064'
	assert entity1.text == 'EGFR-ERBB2'
	assert entity1.position == [(0,10)]

	assert entity2.entityType == 'gene'
	assert entity2.externalID == 'combo|HGNC:3690|HGNC:11524'
	assert entity2.text == 'FGFR3-TACC3'
	assert entity2.position == [(42,53)]

def test_entityrecognizer_fusion_2():
	lookup = makeTestLookup()

	text = 'HER2-neu is a gene.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectFusionGenes=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'HGNC:2064'
	assert entity.text == 'HER2-neu'
	assert entity.position == [(0,8)]

def test_entityrecognizer_merge_brackets_OFF():
	lookup = makeTestLookup()

	text = 'This paper studies non-small cell lung carcinoma (NSCLC).'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 2
	entity1,entity2 = doc.entities
	
	assert entity1.entityType == 'cancer'
	assert entity1.externalID == 'DOID:3908'
	assert entity1.text == 'non-small cell lung carcinoma'
	assert entity1.position == [(19,48)]

	assert entity2.entityType == 'cancer'
	assert entity2.externalID == 'DOID:3908'
	assert entity2.text == 'NSCLC'
	assert entity2.position == [(50,55)]

def test_entityrecognizer_merge_brackets_1():
	lookup = makeTestLookup()

	text = 'This paper studies non-small cell lung carcinoma (NSCLC).'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,mergeTerms=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'cancer'
	assert entity.externalID == 'DOID:3908'
	assert entity.text == 'non-small cell lung carcinoma (NSCLC)'
	assert entity.position == [(19,56)]


if __name__ == '__main__':
	test_entityrecognizer_fusion_2()
