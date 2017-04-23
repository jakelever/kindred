import shlex
import subprocess
import os
from pycorenlp import StanfordCoreNLP
import time
from threading import Thread

directory='/projects/jlever/github/kindred/corenlp/stanford-corenlp-full-2016-10-31'

command='java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000'

os.chdir(directory)
process = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=directory)#, shell=True)
while True:
	#break
	#lineStd = process.stdout.readline()
	#lineStd = ''
	lineErr = process.stderr.readline()
	#if lineS == '':
	#	continue

	if lineErr != '':
		print "X", lineErr.strip()
	
	if 'listening at' in lineErr:
		print "Break";
		break

#time.sleep(15)

def threaded_function(p):
	while True:
		lineErr = p.stderr.readline()
		if lineErr != '':
			print "Y", lineErr.strip()

#thread = Thread(target = threaded_function, args = (process, ), daemon=True)
#thread.start()


print "Opening connection"
nlp = StanfordCoreNLP('http://localhost:9000')

print "Connection made"

text = ( 'Pusheen and Smitha walked along the beach. Pusheen wanted to surf, but fell off the surfboard.')

output = nlp.annotate(text, properties={
		  'annotators': 'tokenize,ssplit,pos,depparse,parse',
		    'outputFormat': 'json'
		      })

print(output['sentences'][0]['parse'])

process.kill()

