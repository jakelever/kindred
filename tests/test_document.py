import kindred

def test_document_str():
	doc1 = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.',loadFromSimpleTag=True)
	expected1 = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' sourceid=T2 [(33, 39)]>] []>"
	
	assert str(doc1) == expected1
	assert doc1.__repr__() == expected1

	doc2 = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.<relation type="causes" subj="T2" obj="T1" />',loadFromSimpleTag=True)
	expected2 = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' sourceid=T2 [(33, 39)]>] [<Relation causes [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' sourceid=T2 [(33, 39)]>] ['obj', 'subj']>]>"
	
	assert str(doc2) == expected2
	assert doc2.__repr__() == expected2

def test_document_init():
	text = "Cancer is caused by mutations in ABCDE1."
	e1 = kindred.Entity('disease','Cancer',[(0,6)],'T1')
	e2 = kindred.Entity('gene','ABCDE1',[(33,39)],'T2')

	doc = kindred.Document(text,[e1,e2])

	expected = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' sourceid=T2 [(33, 39)]>] []>"
	assert str(doc) == expected

def test_document_init_withRel():
	text = "Cancer is caused by mutations in ABCDE1."
	e1 = kindred.Entity('disease','Cancer',[(0,6)],'T1')
	e2 = kindred.Entity('gene','ABCDE1',[(33,39)],'T2')
	rel = kindred.Relation('causes',[e1,e2],['subj','obj'])

	doc = kindred.Document(text,[e1,e2],[rel])

	expected = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' sourceid=T2 [(33, 39)]>] [<Relation causes [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' sourceid=T2 [(33, 39)]>] ['subj', 'obj']>]>"
	assert str(doc) == expected

def test_document_addEntity():
	text = "Cancer is caused by mutations in ABCDE1."

	doc = kindred.Document(text,[])

	e1 = kindred.Entity('disease','Cancer',[(0,6)],'T1')
	doc.addEntity(e1)

	expected = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' sourceid=T1 [(0, 6)]>] []>"
	assert str(doc) == expected

def test_document_splitIntoSentences():
	text = "<drug id='1'>Erlotinib</drug> is an <gene id='2'>EGFR</gene> inhibitor. <drug id='3'>Gefitinib</drug> is another drug. <relation type='inhibits' drug='1' gene='2' />"
	corpus = kindred.Corpus(text,loadFromSimpleTag=True)

	parser = kindred.Parser()
	parser.parse(corpus)

	doc = corpus.documents[0]

	sentenceCorpus = doc.splitIntoSentences()

	assert isinstance(sentenceCorpus,kindred.Corpus)
	assert len(sentenceCorpus.documents) == 2

	expected1 = "<Document Erlotinib is an EGFR inhibitor. [<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, <Entity gene:'EGFR' sourceid=2 [(16, 20)]>] [<Relation inhibits [<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, <Entity gene:'EGFR' sourceid=2 [(16, 20)]>] ['drug', 'gene']>]>"
	expected2 = "<Document Gefitinib is another drug. [<Entity drug:'Gefitinib' sourceid=3 [(0, 9)]>] []>"

	assert str(sentenceCorpus.documents[0]) == expected1
	assert str(sentenceCorpus.documents[1]) == expected2

	doc0 = sentenceCorpus.documents[0]
	assert len(doc0.sentences) == 1

	sentence0 = doc0.sentences[0]
	expectedTokens0 = "('Erlotinib', 'Erlotinib', 'PROPN', 0, 9),('is', 'be', 'VERB', 10, 12),('an', 'an', 'DET', 13, 15),('EGFR', 'EGFR', 'PROPN', 16, 20),('inhibitor', 'inhibitor', 'NOUN', 21, 30),('.', '.', 'PUNCT', 30, 31)"

	assert ",".join(str((t.word,t.lemma,t.partofspeech,t.startPos,t.endPos)) for t in sentence0.tokens).replace("u'","'") == expectedTokens0
	assert str(sentence0.dependencies).replace("u'","'") == "[(1, 0, 'nsubj'), (1, 1, 'ROOT'), (4, 2, 'det'), (4, 3, 'compound'), (1, 4, 'attr'), (1, 5, 'punct')]"
	assert str(sentence0.entityAnnotations) == "[(<Entity drug:'Erlotinib' sourceid=1 [(0, 9)]>, [0]), (<Entity gene:'EGFR' sourceid=2 [(16, 20)]>, [3])]"

	doc1 = sentenceCorpus.documents[1]
	assert len(doc1.sentences) == 1

	sentence1 = doc1.sentences[0]
	expectedTokens1 = "('Gefitinib', 'Gefitinib', 'PROPN', 0, 9),('is', 'be', 'VERB', 10, 12),('another', 'another', 'DET', 13, 20),('drug', 'drug', 'NOUN', 21, 25),('.', '.', 'PUNCT', 25, 26)"
	assert ",".join(str((t.word,t.lemma,t.partofspeech,t.startPos,t.endPos)) for t in sentence1.tokens).replace("u'","'") == expectedTokens1
	assert str(sentence1.dependencies).replace("u'","'") == "[(1, 0, 'nsubj'), (1, 1, 'ROOT'), (3, 2, 'det'), (1, 3, 'attr'), (1, 4, 'punct')]"
	assert str(sentence1.entityAnnotations) == "[(<Entity drug:'Gefitinib' sourceid=3 [(0, 9)]>, [0])]"

