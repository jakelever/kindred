
import kindred
import pytest
import requests

def test_pubannotation():
	# PubAnnotation is an external service (behind Cloudflare) that may refuse requests from CI machines, so skip rather than fail if it's unavailable
	try:
		corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')
	except (RuntimeError, requests.exceptions.RequestException) as e:
		pytest.skip("PubAnnotation unavailable: %s" % e)

	assert isinstance(corpus,kindred.Corpus)

	fileCount = len(corpus.documents)
	entityCount = sum([ len(d.entities) for d in corpus.documents ])
	relationCount = sum([ len(d.relations) for d in corpus.documents ])

	assert fileCount > 0
	assert relationCount > 0
	assert entityCount > 0
	
if __name__ == '__main__':
	test_pubannotation()
