import kindred

def test_entity_str():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16")

	expected1 = "<Entity drug:'Erlotinib' id=%d sourceid=None [(0, 9)]>" % e1.entityID
	expected2 = "<Entity drug:'Erlotinib' id=%d sourceid=T16 [(0, 9)]>" % e2.entityID
	assert str(e1) == expected1
	assert str(e2) == expected2


def test_entity_repr():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16")

	expected1 = "<Entity drug:'Erlotinib' id=%d sourceid=None [(0, 9)]>" % e1.entityID
	expected2 = "<Entity drug:'Erlotinib' id=%d sourceid=T16 [(0, 9)]>" % e2.entityID
	assert e1.__repr__() == expected1
	assert e2.__repr__() == expected2

def test_entity_equals():
	e1 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)
	e2 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID="T16")
	e3 = kindred.Entity(entityType="drug",text="Erlotinib",position=[(0,9)],sourceEntityID=None)

	assert e1 == e1
	assert e1 != e2
	assert e1 != e3
	assert e2 == e2
	assert e2 != e3

