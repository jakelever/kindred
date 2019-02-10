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
