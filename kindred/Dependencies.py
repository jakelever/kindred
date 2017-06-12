
import zipfile
import hashlib
import os
import sys
import wget
import subprocess
import shlex
import time
import atexit
from nltk.parse import malt

if sys.version_info >= (3, 0):
	import urllib.request
else:
	import urllib

def _calcSHA256(filename):
	return hashlib.sha256(open(filename, 'rb').read()).hexdigest()

def _findFile(name, path):
	for root, dirs, files in os.walk(path):
		if name in files:
			return os.path.abspath(os.path.join(root, name))
	return None
	
def _findDir(name, path):
	for root, dirs, files in os.walk(path):
		if name in dirs:
			return os.path.abspath(os.path.join(root, name))
	return None

homeDirectory = os.path.expanduser('~')
downloadDirectory = os.path.join(homeDirectory,'.kindred')
def _downloadFiles(files):
	global downloadDirectory
	
	if not os.path.isdir(downloadDirectory):
		os.mkdir(downloadDirectory)
	
	for url,shortName,expectedSHA256 in files:
		downloadedPath = os.path.join(downloadDirectory,shortName)
		if not os.path.isfile(downloadedPath):
		
			try:
				print("Downloading %s" % shortName)
				wget.download(url,out=downloadedPath,bar=None)
				
				downloadedSHA256 = _calcSHA256(downloadedPath)
				assert downloadedSHA256 == expectedSHA256
				
				if shortName.endswith('.zip'):
					print("Unzipping %s" % shortName)
					zip_ref = zipfile.ZipFile(downloadedPath, 'r')
					zip_ref.extractall(downloadDirectory)
					zip_ref.close()
			except:
				exc_info = sys.exc_info()
				if os.path.isfile(downloadedPath):
					os.remove(downloadedPath)
				#raise exc_info[0], exc_info[1], exc_info[2]
				# TODO: Make this work in Python2/3 nicely
				print("ERROR: ",exc_info)
				sys.exit(255)
			

corenlpProcess = None
def killCoreNLP():
	if not corenlpProcess is None:
		corenlpProcess.kill()

def checkCoreNLPDownload():
	directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	return not directory is None

def downloadCoreNLP():
	directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	if directory is None:
		files = []
		files.append(('http://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip','stanford-corenlp-full-2016-10-31.zip','753dd5aae1ea4ba14ed8eca46646aef06f6808a9ce569e52a09840f6928d00d8'))
		
		print("Downloading CoreNLP to %s" % downloadDirectory)
		_downloadFiles(files)
		directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
		assert not directory is None, "Error after downloading, could not find corenlp directory"
		print ("Download complete.")
	else:
		print ("CoreNLP is already downloaded. No need to download")


def initializeCoreNLP():
	global corenlpProcess

	directory = _findDir('stanford-corenlp-full-2016-10-31',downloadDirectory)
	if directory is None:
		raise RuntimeError("Could not find  the Stanford CoreNLP files. Use kindred.downloadCoreNLP() first")

	command='java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 150000'

	os.chdir(directory)
	corenlpProcess = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)#, shell=True)

	atexit.register(killCoreNLP)

	while True:
		line = corenlpProcess.stderr.readline()
		line = str(line)
		if line == '':
			continue
		
		print("X", line.strip())
		if line.find('listening') != -1:
			break

	time.sleep(1)
		
	
