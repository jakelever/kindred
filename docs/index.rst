Welcome to kindred documentation!
=================================

.. currentmodule:: kindred

Overview
--------

Kindred is a Python package specifically designed for binary relation extraction from biomedical texts (e.g. Pubmed abstracts). It takes a supervised learning approach, and therefore requires training data in order to build a model. 

Kindred does not do entity extracton, but has integration with Pubtator to automatically pull out Pubmed abstracts with a number of entities tagged. It is also integrated with Pubannotation and can easily load annotation data

Installation
------------

Kindred is distributed through PyPI. Hence you should be able to install it with the shell command below.

.. code:: bash

   pip install kindred

If you need to upgrade to a newer release, use the following shell command.

.. code:: bash
   
   pip install --upgrade kindred

And if you want to install directly from source, using this shell command.

.. code:: bash

   python setup.py install

Once it is installed, Kindred can be imported in Python with:

>>> import kindred

Running Stanford CoreNLP
~~~~~~~~~~~~~~~~~~~~~~~~

The Stanford CoreNLP framework is an important dependency of Kindred. All other dependencies of Kindred are managed by the pip/setup.py install. Stanford CoreNLP can be run as a local server and Kindred will connect to it for all parsing needs. 

If you don't have a CoreNLP server running and would like Kindred to take care of it, use the command below. This will download the required CoreNLP distribution and launch a subprocess as needed by Kindred. This subprocess will be killed when Kindred stops.

>>> import kindred
>>> kindred.downloadCoreNLP()

If you already have a Stanford CoreNLP server running, you will need to give the Parser class the relevant address.

>>> import kindred
>>> parser = kindred.Parser(URL_WITH_PORT_HERE)

Getting Started
---------------

Let's walk through a basic example for the BioNLP Shared Task. This will involve loading a corpus of data to train a classifier and a corpus to make predictions on and for evaluation. We will then train the classifier, make the predictions and evaluate how we did. The smaller steps (parsing, candidate building & vectorizing) are done behind the scenes.

First we need to load the data. We want the training and development corpus and use the commands below

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

Frequently Asked Questions
--------------------------

Citing
------

Reference
---------

Main components
~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Parser
   CandidateBuilder
   Vectorizer
   RelationClassifier

Data types
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Corpus
   Document
   Relation
   Entity
   Sentence
   Token

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

   loadDoc
   loadDocs
   loadDir
   save
   evaluate

