Kindred
--------

|build-status| |coverage| |docs| |license|

.. |build-status| image:: https://travis-ci.org/jakelever/kindred.svg?branch=master
   :target: https://travis-ci.org/jakelever/kindred
   :alt: Travis CI status

.. |coverage| image:: https://coveralls.io/repos/github/jakelever/kindred/badge.svg?branch=master
   :target: https://coveralls.io/github/jakelever/kindred?branch=master
   :alt: Coverage status
   
.. |docs| image:: https://readthedocs.org/projects/kindred/badge/
   :target: http://kindred.readthedocs.io/
   :alt: Documentation status
   
.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT license

Kindred is a package for relation extraction in biomedical texts. Given some training data, it can build a model to identify relations between entities (e.g. drugs, genes, etc) in a sentence.

Install
-------

Kindred relies on the Stanford CoreNLP toolkit for parsing. By default it will attempt to connect to a local server (localhost:9000). If you want Kindred to download the CoreNLP files and run it as a subprocess when a server can't be found, use the following command:

>>> import kindred
>>> kindred.downloadCoreNLP()

Usage
-----

BioNLP Shared Task Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> trainCorpus = kindred.bionlpst.load('2016-BB3-event-train')
>>> devCorpus = kindred.bionlpst.load('2016-BB3-event-dev')
>>> predictionCorpus = devCorpus.clone()
>>> predictionCorpus.removeRelations()
>>> classifier = kindred.RelationClassifier()
>>> classifier.train(trainCorpus)
>>> classifier.predict(predictionCorpus)
>>> f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')

PubAnnotation Example
~~~~~~~~~~~~~~~~~~~~~

>>> corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')

PubTator Example
~~~~~~~~~~~~~~~~

>>> corpus = kindred.pubtator.load([19894120,19894121])
