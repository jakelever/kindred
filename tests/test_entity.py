import kindred

def test_entity_str():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16")

	expected1 = "<Entity drug:'Erlotinib' sourceid=None [(0, 9)]>"
	expected2 = "<Entity drug:'Erlotinib' sourceid=T16 [(0, 9)]>"
	assert str(e1) == expected1
	assert str(e2) == expected2

def test_entity_str_withExternalID():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None, externalID="id:1234")
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16", externalID="id:9876")

	expected1 = "<Entity drug:'Erlotinib' sourceid=None externalid=id:1234 [(0, 9)]>" 
	expected2 = "<Entity drug:'Erlotinib' sourceid=T16 externalid=id:9876 [(0, 9)]>"
	assert str(e1) == expected1
	assert str(e2) == expected2


def test_entity_repr():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16")

	expected1 = "<Entity drug:'Erlotinib' sourceid=None [(0, 9)]>"
	expected2 = "<Entity drug:'Erlotinib' sourceid=T16 [(0, 9)]>"
	assert e1.__repr__() == expected1
	assert e2.__repr__() == expected2

def test_entity_equals():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16")
	e3 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	
	rel1 = kindred.Relation(relationType="causes",entities=[e1,e2],argNames=None)

	assert e1 == e1
	assert e1 != e2
	assert e1 != e3
	assert e2 == e2
	assert e2 != e3

	assert e1 != rel1
	assert e2 != rel1
	assert e3 != rel1
