
# Data types
from kindred.Corpus import Corpus
from kindred.Document import Document
from kindred.Entity import Entity
from kindred.Relation import Relation
from kindred.CandidateRelation import CandidateRelation
from kindred.Token import Token
from kindred.Sentence import Sentence

# Components
from kindred.Parser import Parser
from kindred.CandidateBuilder import CandidateBuilder
from kindred.Vectorizer import Vectorizer
from kindred.RelationClassifier import RelationClassifier
from kindred.LogisticRegressionWithThreshold import LogisticRegressionWithThreshold
from kindred.EntityRecognizer import EntityRecognizer

# General functions
from kindred.loadFunctions import loadDoc,loadDocs,loadDir,iterLoadDataFromBioc
from kindred.saveFunctions import save
from kindred.evalFunctions import evaluate

# Data sources
from kindred import bionlpst, pubannotation, pubtator, utils

from kindred.defunctFileWarning import checkForDefunctKindredFiles

checkForDefunctKindredFiles()
