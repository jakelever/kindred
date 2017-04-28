import argparse
import pickle
import sys

import kindred
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.Parser import Parser
from kindred.RelationClassifier import RelationClassifier
from kindred.Evaluator import Evaluator

from kindred.datageneration import generateData,generateTestData

from kindred.DataLoad import loadDataFromSTFormat_Directory

def assertEntity(entity,expectedType,expectedText,expectedPos,expectedSourceEntityID):
	assert isinstance(entity,kindred.Entity)
	assert entity.entityType == expectedType, "(%s) not as expected" % (entity.__str__())
	assert entity.text == expectedText, "(%s) not as expected" % (entity.__str__())
	assert entity.pos == expectedPos, "(%s) not as expected" % (entity.__str__())
	assert entity.sourceEntityID == expectedSourceEntityID, "(%s) not as expected" % (entity.__str__())

if __name__ == '__main__':
	argparser = argparse.ArgumentParser('Tests for parser')
	argparser.add_argument('--inDir',required=True,type=str,help='Directory with ST files')
	argparser.add_argument('--parser',required=True,type=str,help='Which parser to use (stanford/malt)')
	argparser.add_argument('--outPickle',required=True,type=str,help='Output pickle of parses')
	args = argparser.parse_args()
	
	print "Loading..."
	sys.stdout.flush()
	data = loadDataFromSTFormat_Directory(args.inDir)
	print "Loaded"
	sys.stdout.flush()
	
	print "Parsing..."
	sys.stdout.flush()
	parser = Parser(depparser=args.parser)
	processedSentences = parser.parse(data)
	print "Parsed"
	sys.stdout.flush()
	
	print "Saving..."
	sys.stdout.flush()
	with open(args.outPickle,'wb') as f:
		pickle.dump(processedSentences,f)
	print "Saved"
	sys.stdout.flush()
	