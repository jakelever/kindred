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

Insert description of package here please

Usage
-----

BioNLP Example
~~~~~~~~~~~~~~

>>> import kindred
>>> train_data = kindred.bionlpst.load('2016-BB3-event-training')
>>> dev_data = kindred.bionlpst.load('2016-BB3-event-development')
>>> classifier = kindred.RelationClassifier()
>>> classifier.train(train_data)
>>> predicted_relations = classifier.predict(dev_data)
>>> f1score = kindred.evaluate(dev_data, prediction_relations, metric='f1score')

PubAnnotation Example
~~~~~~~~~~~~~~~~~~~~~

>>> import kindred
>>> train_data = kindred.pubannotation.load('bionlp-st-gro-2013-development')
>>> model = kindred.train(train_data)

PubTator Example
~~~~~~~~~~~~~~~~

>>> import kindred
>>> data = kindred.pubtator.load([19894120,19894121])
