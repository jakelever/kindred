
import kindred

import os
import subprocess
import shlex
import time
import atexit
import tempfile
import requests
import pytest_socket

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
	directory = kindred.utils._findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	return not directory is None

def downloadCoreNLP():
	global downloadDirectory
	directory = kindred.utils._findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	if directory is None:
		files = []
		files.append(('http://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip','stanford-corenlp-full-2016-10-31.zip','753dd5aae1ea4ba14ed8eca46646aef06f6808a9ce569e52a09840f6928d00d8'))
		
		print("Downloading CoreNLP to %s" % downloadDirectory)
		kindred.utils._downloadFiles(files,downloadDirectory)
		directory = kindred.utils._findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
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

	directory = kindred.utils._findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
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
		
