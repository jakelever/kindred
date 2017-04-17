from unittest import TestCase

import kindred

class TestJoke(TestCase):
	def test_is_string(self):
		s = kindred.joke()
		self.assertFalse(isinstance(s, int))

