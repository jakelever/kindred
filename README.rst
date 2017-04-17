Kindred
--------

|build-status| |docs|

.. |build-status| image:: https://travis-ci.org/jakelever/kindred.svg?branch=master
   :target: https://travis-ci.org/jakelever/kindred
   :alt: Travis CI status

.. |docs| image:: https://readthedocs.org/projects/kindred/badge/
   :target: https://readthedocs.org/projects/kindred
   :alt: Documentation status

Insert description of package here please

Installing
----------

.. code:: sh

    pip install kindred

Usage
-----

>>> import kindred
>>> tuples,sentenceData = kindred.capitals
>>> trainData = data[asdasd]
>>> testData = data[asdasddas]
>>> model = kindred.Model()
>>> model.train(trainSentences,trainTuples)
>>> predictions = model.predict(testData)
>>> print kindred.evaluate(trainData,testData)


An example of using kindred from the command line with a set of ST files (e.g. BioNLP task)

