import kindred

def test_relation_hash():
	rel1 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=None)
	rel3 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=["drug","disease"])
	rel4 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=["drug","disease"])

	assert hash(rel1) == hash(rel2)
	assert hash(rel3) == hash(rel4)
	assert hash(rel1) != hash(rel3)

	assert hash(rel1) == hash((rel1.relationType,tuple(rel1.entityIDs)))
	assert hash(rel3) == hash((rel3.relationType,tuple(rel3.entityIDs),tuple(rel3.argNames)))

def test_relation_str():
	rel1 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=["drug","disease"])

	expected1 = "<Relation causes [1, 2] None>"
	expected2 = "<Relation causes [1, 2] ['drug', 'disease']>"

	assert str(rel1) == expected1
	assert str(rel2) == expected2

def test_relation_repr():
	rel1 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=["drug","disease"])

	expected1 = "<Relation causes [1, 2] None>"
	expected2 = "<Relation causes [1, 2] ['drug', 'disease']>"

	assert rel1.__repr__() == expected1
	assert rel2.__repr__() == expected2

def test_relation_equals():
	rel1 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=None)
	rel2 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=None)
	rel3 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=["drug","disease"])
	rel4 = kindred.Relation(relationType="causes",entityIDs=[1,2],argNames=["drug","disease"])
	
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

