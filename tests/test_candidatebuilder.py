import kindred
from kindred.CandidateBuilder import CandidateBuilder

from kindred.datageneration import generateData,generateTestData
	
def test_simpleRelationCandidates():
	text = "<drug id=1>Erlotinib</drug> is a common treatment for <cancer id=2>NSCLC</cancer>. <drug id=3>Aspirin</drug> is the main cause of <disease id=4>boneitis</disease> ."
	relations = [ ('treats',1,2) ]

	data = [kindred.RelationData(text,relations)]	
	
	candidateBuilder = CandidateBuilder()
	relTypes,candidateRelations,candidateClasses = candidateBuilder.build(data)
	
	assert relTypes == [('treats', 2)]
	assert candidateClasses == [[1], [0], [0], [0]]
	assert len(candidateRelations) == 4
	
	assert str(candidateRelations[0].processedSentence) == 'Erlotinib is a common treatment for NSCLC .'
	assert str(candidateRelations[1].processedSentence) == 'Erlotinib is a common treatment for NSCLC .'
	assert str(candidateRelations[2].processedSentence) == 'Aspirin is the main cause of boneitis .'
	assert str(candidateRelations[3].processedSentence) == 'Aspirin is the main cause of boneitis .'
	
	assert candidateRelations[0].entitiesInRelation == (1, 2)
	assert candidateRelations[1].entitiesInRelation == (2, 1)
	assert candidateRelations[2].entitiesInRelation == (3, 4)
	assert candidateRelations[3].entitiesInRelation == (4, 3)
