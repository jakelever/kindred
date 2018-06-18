import kindred
import pytest

def test_evaluate(capfd):
	goldText = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene>. We also studied <disease id="T3">glioblastoma</disease>.'
	goldText += '<relation type="typeA" subj="T2" obj="T1" />'
	goldText += '<relation type="typeB" subj="T2" obj="T3" />'
	goldText += '<relation type="typeA" subj="T3" obj="T1" />'
	goldText += '<relation type="typeB" subj="T2" obj="T1" />'
	goldText += '<relation type="typeC" subj="T2" obj="T1" />'

	goldCorpus = kindred.Corpus(goldText,loadFromSimpleTag=True)
	
	testCorpus = goldCorpus.clone()
	testDoc = testCorpus.documents[0]
	mapping = { entity.sourceEntityID:entity for entity in testDoc.entities }
	
	# Remove a relation and add two different ones
	testDoc.relations = testDoc.relations[:4]
	testDoc.addRelation(kindred.Relation("typeX",entities=[mapping["T1"],mapping["T2"]]))
	testDoc.addRelation(kindred.Relation("typeX",entities=[mapping["T1"],mapping["T3"]]))

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
	
	# Make sure nothing has been displayed
	out, err = capfd.readouterr()
	assert out == ""
	assert err == ""

def test_evaluate_display(capfd):
	goldText = 'The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene>. We also studied <disease id="T3">glioblastoma</disease>.'
	goldText += '<relation type="typeA" subj="T2" obj="T1" />'
	goldText += '<relation type="typeB" subj="T2" obj="T3" />'
	goldText += '<relation type="typeA" subj="T3" obj="T1" />'
	goldText += '<relation type="typeB" subj="T2" obj="T1" />'
	goldText += '<relation type="typeC" subj="T2" obj="T1" />'

	goldCorpus = kindred.Corpus(goldText,loadFromSimpleTag=True)
	
	testCorpus = goldCorpus.clone()
	testDoc = testCorpus.documents[0]
	mapping = { entity.sourceEntityID:entity for entity in testDoc.entities }
	
	# Remove a relation and add two different ones
	testDoc.relations = testDoc.relations[:4]
	testDoc.addRelation(kindred.Relation("typeX",entities=[mapping["T1"],mapping["T2"]]))
	testDoc.addRelation(kindred.Relation("typeX",entities=[mapping["T1"],mapping["T3"]]))

	_,_,_ = kindred.evaluate(goldCorpus,testCorpus,metric='all',display=True)
	
	out, err = capfd.readouterr()
	expected = "typeA\tTP:2 FP:0 FN:0\tP:1.000000 R:1.000000 F1:1.000000\ntypeB\tTP:2 FP:0 FN:0\tP:1.000000 R:1.000000 F1:1.000000\ntypeC\tTP:0 FP:0 FN:1\tP:0.000000 R:0.000000 F1:0.000000\ntypeX\tTP:0 FP:2 FN:0\tP:0.000000 R:0.000000 F1:0.000000\n--------------------------------------------------\nAll  \tTP:4 FP:2 FN:1\tP:0.666667 R:0.800000 F1:0.727273\n"
	assert out == expected
	assert err == ""

