import kindred

def test_sentence_noDependencyInfo(capfd):
	text = 'mutations cause dangerous cancer'
	tokens = [ kindred.Token(w,None,None,0,0) for w in text.split() ]

	s = kindred.Sentence(tokens,dependencies=[],entitiesWithLocations=[])

	nodes,edges = s.extractMinSubgraphContainingNodes([0,2])
	out, err = capfd.readouterr()
	assert err.strip() == 'WARNING. 2 node(s) not found in dependency graph!'
	assert nodes == set()
	assert edges == set()

def test_sentence_brokenDependencyPath(capfd):
	text = 'mutations cause dangerous cancer'
	tokens = [ kindred.Token(w,None,None,0,0) for w in text.split() ]

	s = kindred.Sentence(tokens,dependencies=[(0,1,'a'),(2,3,'b')],entitiesWithLocations=[])

	nodes,edges = s.extractMinSubgraphContainingNodes([0,2])
	out, err = capfd.readouterr()
	assert err.strip() == 'WARNING. No path found between nodes 0 and 2!'
	assert nodes == set()
	assert edges == set()

def test_sentence_workingDependencyPath(capfd):
	text = 'lots of mutations cause dangerous cancer'
	tokens = [ kindred.Token(w,None,None,0,0) for w in text.split() ]

	s = kindred.Sentence(tokens,dependencies=[(2,3,'a'),(3,5,'b'),(4,5,'c')],entitiesWithLocations=[])

	nodes,edges = s.extractMinSubgraphContainingNodes([2,5])
	assert nodes == set([2,3,5])
	assert edges == set([(2, 3, 'a'), (3, 5, 'b')])

def test_sentence_workingDependencyPath(capfd):
	text = 'lots of mutations cause dangerous cancer'
	tokens = [ kindred.Token(w,None,None,0,0) for w in text.split() ]

	e1 = kindred.Entity('thingA','mutations',[(0,1)])
	e2 = kindred.Entity('thingB','cancer',[(0,1)])

	entitiesWithLocations = [ (e1,[2]), (e2,[5]) ]

	s = kindred.Sentence(tokens,dependencies=[(2,3,'a'),(3,5,'b'),(4,5,'c')],entitiesWithLocations=entitiesWithLocations)

	assert s.getEntityType(e1.entityID) == 'thingA'
	assert s.getEntityType(e2.entityID) == 'thingB'

def test_sentence_str(capfd):
	text = 'lots of mutations cause dangerous cancer'
	tokens = [ kindred.Token(w,None,None,0,0) for w in text.split() ]

	e1 = kindred.Entity('thingA','mutations',[(0,1)])
	e2 = kindred.Entity('thingB','cancer',[(0,1)])

	entitiesWithLocations = [ (e1,[2]), (e2,[5]) ]

	s = kindred.Sentence(tokens,dependencies=[(2,3,'a'),(3,5,'b'),(4,5,'c')],entitiesWithLocations=entitiesWithLocations)

	assert str(s) == "lots of mutations cause dangerous cancer"

def test_sentence_str(capfd):
	text = 'lots of mutations cause dangerous cancer'
	tokens = [ kindred.Token(w,None,None,0,0) for w in text.split() ]

	e1 = kindred.Entity('thingA','mutations',[(0,1)])
	e2 = kindred.Entity('thingB','cancer',[(0,1)])

	entitiesWithLocations = [ (e1,[2]), (e2,[5]) ]

	s = kindred.Sentence(tokens,dependencies=[(2,3,'a'),(3,5,'b'),(4,5,'c')],entitiesWithLocations=entitiesWithLocations)

	assert s.__repr__() == "lots of mutations cause dangerous cancer"
