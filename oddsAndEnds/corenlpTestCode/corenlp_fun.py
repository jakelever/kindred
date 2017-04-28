import subprocess
import os
from pycorenlp import StanfordCoreNLP
import time
import json

nlp = StanfordCoreNLP('http://localhost:9000')

for _ in range(1):
	text = ( 'Pusheen and Smitha walked along the beach. Pusheen wanted to surf, but fell off the surfboard.')

	output = nlp.annotate(text, properties={
			  'annotators': 'tokenize,ssplit,lemma,pos,depparse,parse',
			    'outputFormat': 'json'
			      })

	print(output['sentences'][0]['parse'])
	print(json.dumps(output,indent=2,sort_keys=True))

	break

