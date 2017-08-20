# Temporary inclusion of pycorenlp code for easier edits
# https://github.com/smilli/py-corenlp

import json, requests
import six

class StanfordCoreNLP:

	useSessions = False
	sessions = {}

	def __init__(self, server_url):
		self.server_url = server_url
		if StanfordCoreNLP.useSessions:
			if not server_url in StanfordCoreNLP.sessions:
				StanfordCoreNLP.sessions[server_url] = requests.Session()
			self.session = StanfordCoreNLP.sessions[server_url]

	def annotate(self, text, properties={}):
		assert isinstance(text, six.string_types),"text must be a string, received %s" % (str(type(text)))
		assert isinstance(properties, dict)
		#print('X',text)

		data = text.encode('utf8')
		
		if StanfordCoreNLP.useSessions:
			r = self.session.post(
				self.server_url, params={
					'properties': str(properties)
				}, data=data, headers={'Connection': 'close'})
		else:
			r = requests.post(
				self.server_url, params={
					'properties': str(properties)
				}, data=data, headers={'Connection': 'close'})
		
		assert 'outputFormat' in properties and properties['outputFormat'] == 'json'
		output = json.loads(r.text, encoding='utf-8', strict=False)

		return output

