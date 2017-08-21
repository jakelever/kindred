
import kindred

import os
import subprocess
import shlex
import time
import atexit
import tempfile
import requests
import pytest_socket
import sys

homeDirectory = os.path.expanduser('~')
downloadDirectory = os.path.join(homeDirectory,'.kindred')
	
corenlpProcess = None
stdoutFile = None
stderrFile = None
			
def killCoreNLP():
	global corenlpProcess
	global stdoutFile
	global stderrFile
	if not corenlpProcess is None:
		corenlpProcess.kill()
		stdoutFile.close()
		stderrFile.close()

		corenlpProcess = None
		stdoutFile = None
		stderrFile = None

def checkCoreNLPDownload():
	directory = kindred.utils._findDir('stanford-corenlp-full-2017-06-09',downloadDirectory)
	return not directory is None

def downloadCoreNLP():
	global downloadDirectory
	directory = kindred.utils._findDir('stanford-corenlp-full-2017-06-09',downloadDirectory)
	if directory is None:
		files = []
		files.append(('http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip','stanford-corenlp-full-2017-06-09.zip','7fb27a0e8dd39c1a90e4155c8f27cd829956e8b8ec6df76b321c04b1fe887961'))
		
		print("Downloading CoreNLP to %s" % downloadDirectory)
		sys.stdout.flush()
		kindred.utils._downloadFiles(files,downloadDirectory)
		directory = kindred.utils._findDir('stanford-corenlp-full-2017-06-09',downloadDirectory)
		assert not directory is None, "Error after downloading, could not find corenlp directory"
		print ("Download complete.")
	else:
		print ("CoreNLP is already downloaded. No need to download")


def testCoreNLPConnection():
	try:
		requests.get('http://localhost:9000')
		return True
	except requests.exceptions.ConnectionError:
		return False
	except pytest_socket.SocketBlockedError:
		return False

def initializeCoreNLP():
	global corenlpProcess
	global stdoutFile
	global stderrFile

	if testCoreNLPConnection():
		return

	directory = kindred.utils._findDir('stanford-corenlp-full-2017-06-09',downloadDirectory)
	if directory is None:
		raise RuntimeError("Could not find the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first")

	command='java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 150000'

	os.chdir(directory)

	stdoutFile = tempfile.NamedTemporaryFile(delete=True)
	stderrFile = tempfile.NamedTemporaryFile(delete=True)

	corenlpProcess = subprocess.Popen(shlex.split(command), stdout=stdoutFile, stderr=stderrFile, cwd=directory)#, shell=True)

	atexit.register(killCoreNLP)

	maxTries = 10

	connectionSuccess = False
	for tries in range(maxTries):
		if testCoreNLPConnection():
			connectionSuccess = True
			break
		time.sleep(5)

	if not connectionSuccess:
		killCoreNLP()
		raise RuntimeError("Unable to connect to launched CoreNLP subprocess")

	time.sleep(1)
		
