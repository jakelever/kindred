
import zipfile
import hashlib
import os
import sys
import wget
import subprocess
import shlex
import time
import atexit
import tempfile
import requests
import pytest_socket

if sys.version_info >= (3, 0):
	import urllib.request
else:
	import urllib

homeDirectory = os.path.expanduser('~')
downloadDirectory = os.path.join(homeDirectory,'.kindred')
	
corenlpProcess = None
stdoutFile = None
stderrFile = None

def _calcSHA256(filename):
	return hashlib.sha256(open(filename, 'rb').read()).hexdigest()

def _findDir(name, path):
	for root, dirs, files in os.walk(path):
		if name in dirs:
			return os.path.abspath(os.path.join(root, name))
	return None

def _downloadFiles(files):
	global downloadDirectory
	
	if not os.path.isdir(downloadDirectory):
		os.mkdir(downloadDirectory)
	
	for url,shortName,expectedSHA256 in files:
		downloadedPath = os.path.join(downloadDirectory,shortName)
		
		# Check if the file is already downloaded (and delete if the SHA256 doesn't match)
		if os.path.isfile(downloadedPath):
			downloadedSHA256 = _calcSHA256(downloadedPath)
			if not downloadedSHA256 == expectedSHA256:
				os.remove(downloadedPath)

		if not os.path.isfile(downloadedPath):
			print("Downloading %s" % shortName)
			wget.download(url,out=downloadedPath,bar=None)
			
			downloadedSHA256 = _calcSHA256(downloadedPath)
			assert downloadedSHA256 == expectedSHA256
			
			if shortName.endswith('.zip'):
				print("Unzipping %s" % shortName)
				zip_ref = zipfile.ZipFile(downloadedPath, 'r')
				zip_ref.extractall(downloadDirectory)
				zip_ref.close()
			
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
	directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	return not directory is None

def downloadCoreNLP():
	directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	if directory is None:
		files = []
		#files.append(('http://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip','stanford-corenlp-full-2016-10-31.zip','753dd5aae1ea4ba14ed8eca46646aef06f6808a9ce569e52a09840f6928d00d8'))
		files.append(('http://bcgsc.ca/downloads/jlever/stanford-corenlp-full-2016-10-31.zip','stanford-corenlp-full-2016-10-31.zip','753dd5aae1ea4ba14ed8eca46646aef06f6808a9ce569e52a09840f6928d00d8'))
		
		print("Downloading CoreNLP to %s" % downloadDirectory)
		_downloadFiles(files)
		directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
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

	directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
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
		
