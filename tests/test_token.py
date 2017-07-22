import kindred

def test_token_str():
	t = kindred.Token(word="hat",lemma="hat",partofspeech="NN",startPos=0,endPos=3)

	assert str(t) == "hat"

def test_token_repr():
	t = kindred.Token(word="hat",lemma="hat",partofspeech="NN",startPos=0,endPos=3)

	assert t.__repr__()  == "hat"
