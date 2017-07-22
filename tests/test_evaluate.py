import kindred
import pytest

def test_evaluate():
	goldText = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene>. We also studied <disease id="T3">glioblastoma</disease>.'
	goldText += '<relation type="typeA" subj="T2" obj="T1" />'
	goldText += '<relation type="typeB" subj="T2" obj="T3" />'
	goldText += '<relation type="typeA" subj="T3" obj="T1" />'
	goldText += '<relation type="typeB" subj="T2" obj="T1" />'
	goldText += '<relation type="typeC" subj="T2" obj="T1" />'

	goldCorpus = kindred.Corpus(goldText)
	
	testCorpus = goldCorpus.clone()
	testDoc = testCorpus.documents[0]
	mapping = testDoc.getSourceEntityIDsToEntityIDs()
	
	# Remove a relation and add two different ones
	testDoc.relations = testDoc.relations[:4]
	testDoc.addRelation(kindred.Relation("typeX",entityIDs=[mapping["T1"],mapping["T2"]]))
	testDoc.addRelation(kindred.Relation("typeX",entityIDs=[mapping["T1"],mapping["T3"]]))

	precision = kindred.evaluate(goldCorpus,testCorpus,metric='precision')
	assert precision == 4.0/6.0
	recall = kindred.evaluate(goldCorpus,testCorpus,metric='recall')
	assert recall == 4.0/5.0
	f1score = kindred.evaluate(goldCorpus,testCorpus,metric='f1score')
	assert round(f1score,10) == round(72.0/99.0,10)

	precision2,recall2,f1score2 = kindred.evaluate(goldCorpus,testCorpus,metric='all')
	assert precision2 == 4.0/6.0
	assert recall2 == 4.0/5.0
	assert round(f1score2,10) == round(72.0/99.0,10)


	with pytest.raises(RuntimeError) as excinfo:
		kindred.evaluate(goldCorpus,testCorpus,metric='nonsense')
	assert excinfo.value.args == ('Unknown metric: nonsense',)
