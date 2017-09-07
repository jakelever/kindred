import kindred

def test_document_str():
	doc1 = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.')
	mapping1 = doc1.getSourceEntityIDsToEntityIDs()
	expected1 = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' id=%d sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' id=%d sourceid=T2 [(33, 39)]>] []>" % (mapping1["T1"],mapping1["T2"])
	
	assert str(doc1) == expected1
	assert doc1.__repr__() == expected1

	doc2 = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.<relation type="causes" subj="T2" obj="T1" />')
	mapping2 = doc2.getSourceEntityIDsToEntityIDs()
	expected2 = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' id=%d sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' id=%d sourceid=T2 [(33, 39)]>] [<Relation causes [%d, %d] ['obj', 'subj']>]>" % (mapping2["T1"],mapping2["T2"],mapping2["T1"],mapping2["T2"])
	
	assert str(doc2) == expected2
	assert doc2.__repr__() == expected2


def test_document_entityTypeMap():
	doc = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.')

	mapping = doc.getSourceEntityIDsToEntityIDs()
	expected = {mapping["T1"]:'disease',mapping["T2"]:'gene'}
	assert doc.getEntityIDsToEntityTypes() == expected


def test_document_entitySourceIDToEntityID():
	doc = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.')

	expected = { e.sourceEntityID:e.entityID for e in doc.entities}
	assert doc.getSourceEntityIDsToEntityIDs() == expected
		
def test_document_entityIDToEntitySourceID():
	doc = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.')

	expected = { e.entityID:e.sourceEntityID for e in doc.entities}
	assert doc.getEntityIDsToSourceEntityIDs() == expected

def test_document_entityIDToEntity():
	doc = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.')

	expected = { e.entityID:e for e in doc.entities}
	assert doc.getEntityIDsToEntities() == expected

def test_document_entityIDs():
	doc = kindred.Document('<disease id="T1">Cancer</disease> is caused by mutations in <gene id="T2">ABCDE1</gene>.')

	expected = [ e.entityID for e in doc.entities ]
	assert doc.getEntityIDs() == expected

def test_document_init():
	text = "Cancer is caused by mutations in ABCDE1."
	e1 = kindred.Entity('disease','Cancer',[(0,6)],'T1')
	e2 = kindred.Entity('gene','ABCDE1',[(33,39)],'T2')

	doc = kindred.Document(text,[e1,e2])

	expected = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' id=%d sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' id=%d sourceid=T2 [(33, 39)]>] []>" % (e1.entityID,e2.entityID)
	assert str(doc) == expected

def test_document_init_withRel():
	text = "Cancer is caused by mutations in ABCDE1."
	e1 = kindred.Entity('disease','Cancer',[(0,6)],'T1')
	e2 = kindred.Entity('gene','ABCDE1',[(33,39)],'T2')
	rel = kindred.Relation('causes',["T2","T1"],['subj','obj'])

	doc = kindred.Document(text,[e1,e2],[rel])

	expected = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' id=%d sourceid=T1 [(0, 6)]>, <Entity gene:'ABCDE1' id=%d sourceid=T2 [(33, 39)]>] [<Relation causes [%d, %d] ['subj', 'obj']>]>" % (e1.entityID,e2.entityID,e2.entityID,e1.entityID)
	assert str(doc) == expected

def test_document_addEntity():
	text = "Cancer is caused by mutations in ABCDE1."

	doc = kindred.Document(text,[])

	e1 = kindred.Entity('disease','Cancer',[(0,6)],'T1')
	doc.addEntity(e1)

	expected = "<Document Cancer is caused by mutations in ABCDE1. [<Entity disease:'Cancer' id=%d sourceid=T1 [(0, 6)]>] []>" % (e1.entityID)
	assert str(doc) == expected
