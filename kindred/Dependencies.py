import urllib
import zipfile
import hashlib
import os

def calcSHA256(filename):
	return hashlib.sha256(open(filename, 'rb').read()).hexdigest()

def findFile(name, path):
	for root, dirs, files in os.walk(path):
		if name in files:
			return os.path.abspath(os.path.join(root, name))

stanfordParserInitialised = False
def initializeStanfordParser():
	global stanfordParserInitialised
	if not stanfordParserInitialised:
		
		# https://nlp.stanford.edu/software/stanford-parser-full-2016-10-31.zip
		# https://nlp.stanford.edu/software/stanford-english-corenlp-2016-10-31-models.jar
		
		files = []
		files.append(('http://bcgsc.ca/downloads/jlever/stanford-parser-full-2016-10-31.zip','stanford-parser-full-2016-10-31.zip','a019c3909c71ee83ec0ea63e669f8ac6b3bc3fe23b466726424db99697bb16de'))
		
		downloadDirectory = 'downloaded'
		if not os.path.isdir(downloadDirectory):
			os.mkdir(downloadDirectory)
		
		for url,shortName,expectedSHA256 in files:
			downloadedPath = os.path.join(downloadDirectory,shortName)
			if not os.path.isfile(downloadedPath):
			
				try:
					downloadedFile = urllib.URLopener()
					print("Downloading %s" % shortName)
					downloadedFile.retrieve(url,downloadedPath)
				
					downloadedSHA256 = calcSHA256(downloadedPath)
					assert downloadedSHA256 == expectedSHA256
					
					if shortName.endswith('.zip'):
						print "Unzipping %s" % shortName
						zip_ref = zipfile.ZipFile(downloadedPath, 'r')
						zip_ref.extractall(downloadDirectory)
						zip_ref.close()
				except:
					exc_info = sys.exc_info()
					if os.path.isfile(downloadedPath):
						os.remove(downloadedPath)
					raise exc_info[0], exc_info[1], exc_info[2]
				
		
		parserJar = findFile('stanford-parser.jar',downloadDirectory)
		modelsJar = findFile('stanford-parser-3.7.0-models.jar',downloadDirectory)
				
		os.environ["CLASSPATH"] += ":%s:%s" % (parserJar,modelsJar)
		
		stanfordParserInitialised = True
		
if __name__ == '__main__':
	initializeStanfordParser()
	