
import tempfile

import kindred


import zipfile
import hashlib
import os
import sys
import wget

if sys.version_info >= (3, 0):
	import urllib.request
else:
	import urllib

from kindred.DataLoad import loadDataFromSTFormat_Directory

def _calcSHA256(filename):
	return hashlib.sha256(open(filename, 'rb').read()).hexdigest()

def _findFile(name, path):
	assert os.path.isdir(path), "Must provide directory as path"
	for root, dirs, files in os.walk(path):
		if name in files:
			return os.path.abspath(os.path.join(root, name))
	return None
	
def _findDir(name, path):
	assert os.path.isdir(path), "Must provide directory as path"
	for root, dirs, files in os.walk(path):
		if name in dirs:
			return os.path.abspath(os.path.join(root, name))
	return None

def _downloadFiles(files,downloadDirectory):
	if not os.path.isdir(downloadDirectory):
		os.mkdir(downloadDirectory)

	if downloadDirectory[-1] != '/':
		downloadDirectory += '/'
	
	for url,shortName,expectedSHA256 in files:
		downloadedPath = os.path.join(downloadDirectory,shortName)
		if not os.path.isfile(downloadedPath):
		
			try:
				print("Downloading %s" % shortName)
				#if sys.version_info >= (3, 0):
				#	urllib.request.urlretrieve(url,downloadedPath)
				#else:
				#	downloadedFile = urllib.URLopener()
				#	downloadedFile.retrieve(url,downloadedPath)
				wget.download(url,out=downloadedPath,bar=None)
				
				downloadedSHA256 = _calcSHA256(downloadedPath)
				assert downloadedSHA256 == expectedSHA256, "SHA256 mismatch with downloaded file: %s" % shortName
				
				if shortName.endswith('.zip'):
					print("Unzipping %s" % shortName)
					#unzippedDir = downloadDirectory + shortName[0:-4]
					#os.mkdir(unzippedDir)
					zip_ref = zipfile.ZipFile(downloadedPath, 'r')
					zip_ref.extractall(path=downloadDirectory)
					zip_ref.close()
			except:
				exc_info = sys.exc_info()
				if os.path.isfile(downloadedPath):
					os.remove(downloadedPath)
				#raise exc_info[0], exc_info[1], exc_info[2]
				# TODO: Make this work in Python2/3 nicely
				print("ERROR: ",exc_info)
				sys.exit(255)

def loadBioNLPData(task):
	tempDir = tempfile.mkdtemp()

	files = [('http://2016.bionlp-st.org/tasks/bb2/BioNLP-ST-2016_BB-event_train.zip','BioNLP-ST-2016_BB-event_train.zip', '3b02adff92d8ba8814c9901f4af7681863569fe40cd0d87914258d48f989bb96')]

	_downloadFiles(files,tempDir)

	mainDir = _findDir('BioNLP-ST-2016_BB-event_train',tempDir)

	relationData = loadDataFromSTFormat_Directory(mainDir)

	return relationData

