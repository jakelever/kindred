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

Installing
----------

.. code:: sh

    pip install kindred

Usage
-----

BioNLP Example
~~~~~~~~~~~~~~

>>> import kindred
>>> train_data = kindred.bionlpst.get_data('2016-BB3-event-training')
>>> dev_data = kindred.bionlpst.get_data('2016-BB3-event-development')
>>> model = kindred.train(train_data)
>>> predicted_relations = model.predict(dev_data.get_text_and_entities())
>>> f1score = kindred.evaluate(dev_data.get_relations(), prediction_relations, metric='f1score')

PubAnnotation Example
~~~~~~~~~~~~~~~~~~~~~

>>> import kindred
>>> train_data = kindred.pubannotation.get_data('2016-SeeDev-binary-training')
>>> model = kindred.train(train_data)
>>> text = 'A SeeDev related text goes here'
>>> predicted_relations = model.predict(text)
>>> print(predicted_relations)


An example of using kindred from the command line with a set of ST files (e.g. BioNLP task)

