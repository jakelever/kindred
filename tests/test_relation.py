import kindred

def test_relation_hash():
	e1 = kindred.Entity('mutation','BRAF V600E mutation',[])
	e2 = kindred.Entity('event','vemurafenib resistance',[])

	rel1 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)
	rel3 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=["drug","disease"])
	rel4 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=["drug","disease"])

	assert hash(rel1) == hash(rel2)
	assert hash(rel3) == hash(rel4)
	assert hash(rel1) != hash(rel3)

	assert hash(rel1) == hash((rel1.relationType,tuple(rel1.entities),rel1.probability))
	assert hash(rel3) == hash((rel3.relationType,tuple(rel3.entities),tuple(rel3.argNames),rel3.probability))

def test_relation_str():
	e1 = kindred.Entity('mutation','BRAF V600E mutation',[])
	e2 = kindred.Entity('event','vemurafenib resistance',[])

	rel1 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=["drug","disease"])

	expected1 = "<Relation causes [<Entity mutation:'BRAF V600E mutation' sourceid=None []>, <Entity event:'vemurafenib resistance' sourceid=None []>] None>"
	expected2 = "<Relation causes [<Entity mutation:'BRAF V600E mutation' sourceid=None []>, <Entity event:'vemurafenib resistance' sourceid=None []>] ['drug', 'disease']>"

	assert str(rel1) == expected1
	assert str(rel2) == expected2

def test_relation_repr():
	e1 = kindred.Entity('mutation','BRAF V600E mutation',[])
	e2 = kindred.Entity('event','vemurafenib resistance',[])

	rel1 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=["drug","disease"])

	expected1 = "<Relation causes [<Entity mutation:'BRAF V600E mutation' sourceid=None []>, <Entity event:'vemurafenib resistance' sourceid=None []>] None>"
	expected2 = "<Relation causes [<Entity mutation:'BRAF V600E mutation' sourceid=None []>, <Entity event:'vemurafenib resistance' sourceid=None []>] ['drug', 'disease']>"

	assert rel1.__repr__() == expected1
	assert rel2.__repr__() == expected2

def test_relation_equals():
	e1 = kindred.Entity('mutation','BRAF V600E mutation',[])
	e2 = kindred.Entity('event','vemurafenib resistance',[])

	rel1 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)
	rel3 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=["drug","disease"])
	rel4 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=["drug","disease"])
	
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)

	assert rel1 == rel2
	assert rel1 != rel3
	assert rel1 != rel4
	assert rel2 != rel3
	assert rel3 == rel4

	assert rel1 != e1
	assert rel2 != e1
	assert rel3 != e1
	assert rel4 != e1

def test_relation_triple_equals():
	e1 = kindred.Entity('mutation','BRAF V600E mutation',[])
	e2 = kindred.Entity('event','vemurafenib resistance',[])
	e3 = kindred.Entity('citation','28028924',[])

	rel1 = kindred.Relation(relationType="causes",entities=[e1,e2,e3],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entities=[e1,e2,e3],argNames=None)
	rel3 = kindred.Relation(relationType="causes",entities=[e1,e2,e3],argNames=["whathappened","whatdiditcause","citation"])
	rel4 = kindred.Relation(relationType="causes",entities=[e1,e2,e3],argNames=["whathappened","whatdiditcause","citation"])

	assert rel1 == rel2
	assert rel1 != rel3
	assert rel1 != rel4
	assert rel2 != rel3
	assert rel3 == rel4

	assert rel1 != e1
	assert rel2 != e1
	assert rel3 != e1
	assert rel4 != e1

