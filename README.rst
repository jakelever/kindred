Kindred
--------

.. image:: https://travis-ci.org/jakelever/kindred.svg?branch=master   
.. image:: https://readthedocs.org/projects/kindred/badge/?version=latest

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

