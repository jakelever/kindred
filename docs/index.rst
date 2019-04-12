Welcome to kindred documentation!
=================================

.. currentmodule:: kindred

.. toctree::
   :maxdepth: 2
   :hidden:

   Home <self>
   fileformats


.. _Home:


Overview
--------

Kindred is a Python package specifically designed for binary relation extraction from biomedical texts (e.g. PubMed abstracts). It takes a supervised learning approach, and therefore requires training data in order to build a model. 

Kindred can do simple dictionary-based entity extraction. It also has integration with Pubtator to automatically pull out PubMed abstracts with a number of entities tagged and with PubAnnotation and can easily load annotation data.

Installation
------------

Kindred is distributed through PyPI. Hence you should be able to install it with the shell command below.

.. code:: bash

   pip install kindred

If you need to upgrade to a newer release, use the following shell command.

.. code:: bash
   
   pip install --upgrade kindred

And if you want to install directly from source, use this shell command.

.. code:: bash

   python setup.py install

Once it is installed, Kindred can be imported in Python with:

>>> import kindred

Installing a Spacy language model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of v2, Kindred uses the Spacy python package for parsing. A language model needs to be installed for the corresponding language using a command similar to below.

.. code:: bash

   python -m spacy download en

Tutorial with a mini annotation problem
---------------------------------------

There is a `tutorial <https://github.com/jakelever/kindred/tree/master/tutorial>`_ with sample code that steps through a small annotation task for extracting capital cities from text. It's on `Github <https://github.com/jakelever/kindred/tree/master/tutorial>`_ and may give you an understanding of the annotations that Kindred needs and how you might go about getting them. Once you've understood the input data, you might want to dive more into the code and the below examples will give you some ideas.

Getting started with code
-------------------------

Let's walk through a basic example for the BioNLP Shared Task. This will involve loading a corpus of data to train a classifier and a corpus to make predictions on and for evaluation. We will then train the classifier, make the predictions and evaluate how we did. The smaller steps (parsing, candidate building & vectorizing) are done behind the scenes.

First, we need to load the data. We want the training and development corpus and use the commands below

>>> trainCorpus = kindred.bionlpst.load('2016-BB3-event-train')
>>> devCorpus = kindred.bionlpst.load('2016-BB3-event-dev')

We're going to build a model for the relations in the training corpus and make predictions on the development corpus. We are going to keep the devCorpus object to make comparisons against, but need a copy of it that doesn't have any relations attached to it. Hence we will clone it and remove the relations. This will contain all the same text and entity annotations as the devCorpus, but no relations.

>>> predictionCorpus = devCorpus.clone()
>>> predictionCorpus.removeRelations()

Now we're going to build the model on the training data with default settings.

>>> classifier = kindred.RelationClassifier()
>>> classifier.train(trainCorpus)

Now we will use this classifier to predict relations in the predictionCorpus object. These new relations will be added to the corpus.

>>> classifier.predict(predictionCorpus)

Lastly, we will evaluate how well we have done. The common measure is F1-score.

>>> f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')

Specific Examples
-----------------

Here we will show some of the individual steps that might be needed.

Loading data from files
~~~~~~~~~~~~~~~~~~~~~~~

You have a directory of data files that you want to load. The files are in the JSON format.

>>> corpus = kindred.load('json','/home/user/data/')

And if it was in another format, you change the dataFormat parameter. Options include: 'standoff' for the standoff format used in the BioNLP Shared Tasks, 'bioc' for BioC files and 'simpletag' if there are a set of SimpleTag XML files. Note that we only use SimpleTag for generating easy test data and not for any large problems.

Loading data from online resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Kindred integrates with several online resources to make it easy to import data. For BioNLP Shared Tasks, you can use the command below:

>>> corpus = kindred.bionlpst.load('2016-BB3-event-dev')

You can currently import data from the '2016-BB3-event' or '2016-SeeDev-binary' shared tasks. Add 'train', 'dev' or 'test' to them. The 'train' and 'dev' corpora contain relations while the 'test' corpus does not.
	
You can import PubMed abstracts annotated by Pubtator with a list of PubMed IDs (or PMIDs for short). These will contain entity annotations but no relations. The command below will import the two articles with those PMIDs.

>>> corpus = kindred.pubtator.load([19894120,19894121])

You can also import text and annotation data from PubAnnotation. In this case, you provide the project name and Kindred will download all the annotations and associated text. For the 'bionlp-st-gro-2013-development' project, the command to import is below. These annotations may include relation information

>>> corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')

Parsing
~~~~~~~

If you want to parse a corpus, you use a Parser object.

>>> parser = kindred.Parser()
>>> parser.parse(corpus)

Candidate Building
~~~~~~~~~~~~~~~~~~

Given a corpus with annotated entities, one may want to generate the set of all candidate relations between two entities within the same text. One can do this for the first set with the command below. Each Sentence object within the corpus will now have a set of candidate relations attached to it.

>>> candidateBuilder = kindred.CandidateBuilder()
>>> candidateBuilder.fit_transform(corpus)

You can easily extract all the candidate relations using the command below:

>>> candidateRelations = corpus.getCandidateRelations()

The corpus contains a list of relation types contained within.

>>> print(corpus.relationTypes)

And if the corpus contains annotated relations, the candidate relations will be assigned a non-zero class index. Hence a candidate relation with class 0 has not been annotated, but a candidate relation with class 1 is of the first relation type in corpus.relationTypes.

Vectorizing
~~~~~~~~~~~

You may want to generate vectors for each candidate relation. The command below will produce the vectorized matrix with the default set of feature types.

>>> vectorizer = kindred.Vectorizer()
>>> trainMatrix = vectorizer.fit_transform(trainCorpus)

Once you've fit the vectorizer to the training set, remember to only use transform for the test set.

>>> testMatrix = vectorizer.transform(testCorpus)

Want to use only specific feature types (of which the options are: entityTypes, unigramsBetweenEntities, bigrams, dependencyPathEdges, dependencyPathEdgesNearEntities)? Use a command like below:

>>> vectorizer = kindred.Vectorizer(featureChoice=['entityTypes','bigrams'])

Frequently Asked Questions
--------------------------

**Does Kindred handle multiple relations that contain the same entities?**

At the moment, no. Kindred will only use the first annotation of a relation.

Release Notes
-------------

Version 2.5.0
-------------
- Will be final Python2 compatible version
- Added MultiLabelClassifier and changed behaviour when multiple relation types are present. They are now predicted independently using separate classifiers. This allows overlapping relations (where the same entities are part of multiple relations).

Version 2.4.0
-------------
- Updates to the loading and saving functionality so that everything is done through kindred.load or kindred.save
- Changed EntityRecognizer logic to use token boundaries and exact string matching instead of matching tokenization (for faster wordlist loading)

Version 2.3.0
-------------
- Add manuallyAnnotate for a simple mechanism to annotate candidate relations
- Add splitIntoSentences for a parsed corpus/document

Version 2.2.0
-------------
- Add CandidateRelation class to distinguish from Relation
- Reworking of API so that Candidate Relations are no longer stored in corpus. Changes across API that will break backwards compatibility
- Fixes to PubTator input

Version 2.1.0
-------------
- Added EntityRecognizer for basic entity extraction
- Relations can now be n-ary, not just binary

Version 2.0.0
-------------
- Large overhaul to replace CoreNLP with Spacy package for easier integration and installation
- Simplified relation classifier functionality by removing feature building and multiclassifier options
- Add functionality for streaming BioC files

Version 1.1.0
~~~~~~~~~~~~~
- Upgraded to new version of Stanford CoreNLP (3.8.0) and added code to manage upgrade
- Changed dependency parsing to use standard CoreNLP dep parser (instead of constituency with a conversion).
- Changed evaluation function to not output specific details by default
- You can now parse with every language in CoreNLP (arabic,chinese,english,french,german,spanish)
- Improved error display for CoreNLP failures

Version 1.0.0
~~~~~~~~~~~~~
- Original release (corresponding to original paper)

Citing
------

If your work makes use of Kindred, it'd be really nice if you cited us.

.. code:: bibtex

   @article{lever2017painless,
            title={Painless {R}elation {E}xtraction with {K}indred},
            author={Lever, Jake and Jones, Steven JM},
            journal={Bio{NLP} 2017},
            pages={176},
            year={2017}
            }



Reference
---------

Main components
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EntityRecognizer
   CandidateBuilder
   Parser
   RelationClassifier
   Vectorizer

Data types
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   CandidateRelation
   Corpus
   Document
   Entity
   Relation
   Sentence
   Token

Machine Learning Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   LogisticRegressionWithThreshold
   MultiLabelClassifier

Data sources
~~~~~~~~~~~~
.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   bionlpst
   pubannotation
   pubtator

Essential functions
~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   load
   iterLoad
   save
   evaluate
   manuallyAnnotate

