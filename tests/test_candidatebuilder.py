import kindred

from kindred.datageneration import generateData,generateTestData
	
def test_candidatebuilder_simple():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	candidateBuilder = kindred.CandidateBuilder()
	candidateBuilder.fit_transform(corpus)
	
	assert corpus.relationTypes == [('treats', 'obj', 'subj')]
	candidateRelations = corpus.getCandidateRelations()
	candidateClasses = corpus.getCandidateClasses()

	assert candidateClasses == [[0], [1], [0], [0]]
	assert len(candidateRelations) == 4
	
	sourceEntityIDsToEntityIDs = corpus.documents[0].getSourceEntityIDsToEntityIDs()

	assert candidateRelations[0].entityIDs == [sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['2']]
	assert candidateRelations[1].entityIDs == [sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['1']]
	assert candidateRelations[2].entityIDs == [sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['4']]
	assert candidateRelations[3].entityIDs == [sourceEntityIDsToEntityIDs['4'], sourceEntityIDsToEntityIDs['3']]

def test_candidatebuilder_acceptedEntityTypes():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <disease id="2">NSCLC</disease>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	candidateBuilder = kindred.CandidateBuilder(acceptedEntityTypes=[('disease','drug')])
	candidateBuilder.fit_transform(corpus)
	
	assert corpus.relationTypes == [('treats', 'obj', 'subj')]
	candidateRelations = corpus.getCandidateRelations()
	candidateClasses = corpus.getCandidateClasses()

	print(candidateRelations)
	assert candidateClasses == [[1], [0]]
	assert len(candidateRelations) == 2
	
	sourceEntityIDsToEntityIDs = corpus.documents[0].getSourceEntityIDsToEntityIDs()

	assert candidateRelations[0].entityIDs == [sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['1']]
	assert candidateRelations[1].entityIDs == [sourceEntityIDsToEntityIDs['4'], sourceEntityIDsToEntityIDs['3']]

def test_candidatebuilder_triple():
	text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer> which targets <gene id="3">EGFR</gene>. <relation type="druginfo" drug="1" disease="2" gene="3" />'

	corpus = kindred.Corpus(text,loadFromSimpleTag=True)
	
	candidateBuilder = kindred.CandidateBuilder(entityCount=3)
	candidateBuilder.fit_transform(corpus)
	
	assert corpus.relationTypes == [('druginfo', 'disease', 'drug', 'gene')]
	candidateRelations = corpus.getCandidateRelations()
	candidateClasses = corpus.getCandidateClasses()

	assert candidateClasses == [[0], [0], [1], [0], [0], [0]]
	assert len(candidateRelations) == 6
	
	sourceEntityIDsToEntityIDs = corpus.documents[0].getSourceEntityIDsToEntityIDs()

	assert candidateRelations[0].entityIDs == [sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['3']]
	assert candidateRelations[1].entityIDs == [sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['2']]
	assert candidateRelations[2].entityIDs == [sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['3']]
	assert candidateRelations[3].entityIDs == [sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['1']]
	assert candidateRelations[4].entityIDs == [sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['1'], sourceEntityIDsToEntityIDs['2']]
	assert candidateRelations[5].entityIDs == [sourceEntityIDsToEntityIDs['3'], sourceEntityIDsToEntityIDs['2'], sourceEntityIDsToEntityIDs['1']]

if __name__ == '__main__':
	test_simpleRelationCandidates()

