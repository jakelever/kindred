import kindred
import os

def makeTestLookup():
	lookup = {}
	lookup[('epidermal','growth','factor','receptor')] = [('gene','HGNC:3236'),('dummy','ID:1234')]
	#lookup[('epidermal','growth','factor','receptor')] = [('gene','HGNC:3236')]
	lookup[('egfr',)] = [('gene','HGNC:3236')]

	lookup[('erbb2',)] = [('gene','HGNC:2064')]
	lookup[('fgfr3',)] = [('gene','HGNC:3690')]
	lookup[('tacc3',)] = [('gene','HGNC:11524')]

	lookup[('her2',)] = [('gene','HGNC:2064')]
	lookup[('neu',)] = [('gene','HGNC:2064')]
	lookup[('neus',)] = [('gene','HGNC:????')]

	lookup[('non','-','small','cell','lung','carcinoma')] = [('cancer','DOID:3908')]
	lookup[('nsclc',)] = [('cancer','DOID:3908')]
	lookup[('dlbcl',)] = [('cancer','DOID:0050745')]
	lookup[('lymphoma',)] = [('cancer','DOID:0060058')]

	lookup[('never','ending','umbrella')] = [('movie','IMDB:9999')]
	lookup[('never','ending','umbrellas')] = [('movie','IMDB:9999')]

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

def test_entityrecognizer_fusion_3():
	lookup = makeTestLookup()

	text = 'EGFR-lymphoma is not anything.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectFusionGenes=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	print(doc.entities)
	assert len(doc.entities) == 2
	entity1,entity2 = doc.entities
	
	assert entity1.entityType == 'gene'
	assert entity1.externalID == 'HGNC:3236'
	assert entity1.text == 'EGFR'
	assert entity1.position == [(0,4)]

	assert entity2.entityType == 'cancer'
	assert entity2.externalID == 'DOID:0060058'
	assert entity2.text == 'lymphoma'
	assert entity2.position == [(5,13)]

def test_entityrecognizer_fusion_4():
	lookup = makeTestLookup()

	text = 'EGFR-banana is not anything.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectFusionGenes=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'HGNC:3236'
	assert entity.text == 'EGFR'
	assert entity.position == [(0,4)]

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

def test_entityrecognizer_merge_brackets_right():
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

def test_entityrecognizer_merge_brackets_left():
	lookup = makeTestLookup()

	text = 'This paper studies (NSCLC) non-small cell lung carcinoma.'
	
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
	assert entity.text == '(NSCLC) non-small cell lung carcinoma'
	assert entity.position == [(19,56)]

def test_entityrecognizer_merge_nobrackets():
	lookup = makeTestLookup()

	text = 'HER2 neu is a gene.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,mergeTerms=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'gene'
	assert entity.externalID == 'HGNC:2064'
	assert entity.text == 'HER2 neu'
	assert entity.position == [(0,8)]

def test_entityrecognizer_acronyms_OFF():
	lookup = makeTestLookup()

	text = 'The Never Ending Umbrella (NEU) is a true classic.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 2
	entity1,entity2 = doc.entities
	
	assert entity1.entityType == 'movie'
	assert entity1.externalID == 'IMDB:9999'
	assert entity1.text == 'Never Ending Umbrella'
	assert entity1.position == [(4,25)]

	assert entity2.entityType == 'gene'
	assert entity2.externalID == 'HGNC:2064'
	assert entity2.text == 'NEU'
	assert entity2.position == [(27,30)]

def test_entityrecognizer_acronyms_bothHaveIDs():
	lookup = makeTestLookup()

	text = 'The Never Ending Umbrella (NEU) is a true classic.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectAcronyms=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'movie'
	assert entity.externalID == 'IMDB:9999'
	assert entity.text == 'Never Ending Umbrella'
	assert entity.position == [(4,25)]

def test_entityrecognizer_acronyms_bothHaveIDs_plural():
	lookup = makeTestLookup()

	text = 'The Never Ending Umbrellas (NEUs) are true classics.'

	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectAcronyms=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'movie'
	assert entity.externalID == 'IMDB:9999'
	assert entity.text == 'Never Ending Umbrellas'
	assert entity.position == [(4,26)]

def test_entityrecognizer_acronyms_acronymHasCorrectID():
	lookup = makeTestLookup()

	text = 'Diffuse large b cell lymphoma (DLBCL) is a challenging research topic.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectAcronyms=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'cancer'
	assert entity.externalID == 'DOID:0050745'
	assert entity.text == 'DLBCL'
	assert entity.position == [(31,36)]

def test_entityrecognizer_acronyms_acronymHasCorrectID_hyphen():
	lookup = makeTestLookup()

	text = 'Diffuse large b-cell lymphoma (DLBCL) is a challenging research topic.'
	
	corpus = kindred.Corpus(text)

	parser = kindred.Parser()
	parser.parse(corpus)

	ner = kindred.EntityRecognizer(lookup,detectAcronyms=True)
	ner.annotate(corpus)

	doc = corpus.documents[0]
	assert len(doc.entities) == 1
	entity = doc.entities[0]
	
	assert entity.entityType == 'cancer'
	assert entity.externalID == 'DOID:0050745'
	assert entity.text == 'DLBCL'
	assert entity.position == [(31,36)]

def test_loadwordlist():
	scriptDir = os.path.dirname(__file__)
	wordlistPath = os.path.join(scriptDir,'data','terms.wordlist')

	lookup = kindred.EntityRecognizer.loadWordlists([('thing',wordlistPath)])

	expected = {(u'term', u'term', u'term'): set([('thing', u'ID5')]), (u'term5',): set([('thing', u'ID4')]), (u'term4',): set([('thing', u'ID3')]), (u'term3',): set([('thing', u'ID3')]), (u'term2',): set([('thing', u'ID2')]), (u'term1',): set([('thing', u'ID1;ID4')]), (u'term-64',): set([('thing', u'ID5')])}

	assert lookup == expected


if __name__ == '__main__':
	test_entityrecognizer_fusion_3()
