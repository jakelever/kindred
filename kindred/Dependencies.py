import urllib
import zipfile
import hashlib
import os
import sys
from nltk.parse import malt

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

downloadDirectory = 'downloaded'
def _downloadFiles(files):
	global downloadDirectory
	
	if not os.path.isdir(downloadDirectory):
		os.mkdir(downloadDirectory)
	
	for url,shortName,expectedSHA256 in files:
		downloadedPath = os.path.join(downloadDirectory,shortName)
		if not os.path.isfile(downloadedPath):
		
			try:
				downloadedFile = urllib.URLopener()
				print("Downloading %s" % shortName)
				downloadedFile.retrieve(url,downloadedPath)
			
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
				
			
stanfordParserInitialised = False
def initializeStanfordParser():
	global downloadDirectory, stanfordParserInitialised
	if not stanfordParserInitialised:
		
		# https://nlp.stanford.edu/software/stanford-parser-full-2016-10-31.zip
		# https://nlp.stanford.edu/software/stanford-english-corenlp-2016-10-31-models.jar
		
		files = []
		files.append(('http://bcgsc.ca/downloads/jlever/stanford-parser-full-2016-10-31.zip','stanford-parser-full-2016-10-31.zip','a019c3909c71ee83ec0ea63e669f8ac6b3bc3fe23b466726424db99697bb16de'))
		
		_downloadFiles(files)
		
		parserJarFile = _findFile('stanford-parser.jar',downloadDirectory)
		assert not parserJarFile is None
		modelsJarFile = _findFile('stanford-parser-3.7.0-models.jar',downloadDirectory)
		assert not modelsJarFile is None
				
		if "CLASSPATH" in os.environ:
			os.environ["CLASSPATH"] = "%s:%s:%s" % (parserJarFile,modelsJarFile,os.environ["CLASSPATH"])
		else:
			os.environ["CLASSPATH"] = "%s:%s" % (parserJarFile,modelsJarFile)
			
		stanfordParserInitialised = True
		
		
maltParserInitialised = False
maltParserSettings = None
def initializeMaltParser():
	global downloadDirectory, maltParserInitialised, maltParserSettings
	if not maltParserInitialised:
		
		# http://maltparser.org/dist/maltparser-1.9.0.zip
		# http://www.maltparser.org/mco/english_parser/engmalt.linear-1.7.mco
		
		files = []
		files.append(('http://bcgsc.ca/downloads/jlever/maltparser-1.9.0.zip','maltparser-1.9.0.zip','665b7310f56c81b41ab480df455b9190c2cd22ad42899c705776120e0f81b81e'))
		files.append(('http://bcgsc.ca/downloads/jlever/engmalt.linear-1.7.mco','engmalt.linear-1.7.mco','398229faf7f7b57224e277fc07e191d98b1dda4a9d43a5754170f12ddc4cb8f0'))
		
		_downloadFiles(files)
		
		parserDir = _findDir('maltparser-1.9.0',downloadDirectory)
		assert not parserDir is None
		modelFile = _findFile('engmalt.linear-1.7.mco',downloadDirectory)
		assert not modelFile is None
						
		maltParserSettings = {'parserDir':parserDir,'modelFile':modelFile}
		print(maltParserSettings)
			
		maltParserInitialised = True
		
def getMaltParser():
	initializeMaltParser()
	parser = malt.MaltParser(maltParserSettings['parserDir'],maltParserSettings['modelFile'])
	return parser
		
if __name__ == '__main__':
	initializeStanfordParser()
	