# Temporary inclusion of pycorenlp code for easier edits
# https://github.com/smilli/py-corenlp

import json, requests
import six

class StanfordCoreNLP:

	def __init__(self, server_url):
		self.server_url = server_url

	def annotate(self, text, properties={}):
		assert isinstance(text, six.string_types),"text must be a string, received %s" % (str(type(text)))
		assert isinstance(properties, dict)

		data = text.encode('utf8')
		
		r = requests.post(
			self.server_url, params={
				'properties': str(properties)
			}, data=data, headers={'Connection': 'close'})
		
		assert 'outputFormat' in properties and properties['outputFormat'] == 'json'

		try:
			output = json.loads(r.text, encoding='utf-8', strict=False)
		except:
			# Output from CoreNLP is not in json.
			message = "CoreNLP Error. Last output (possibly truncated): %s" % r.text[:1000]
			raise RuntimeError(message)

		return output

