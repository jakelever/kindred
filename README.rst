=======
Kindred
=======

|pypi| |build-status| |coverage| |docs| |license|

.. |pypi| image:: https://img.shields.io/pypi/v/kindred.svg
   :target: https://pypi.python.org/pypi/kindred
   :alt: PyPI Release
   
.. |build-status| image:: https://travis-ci.org/jakelever/kindred.svg?branch=master
   :target: https://travis-ci.org/jakelever/kindred
   :alt: Travis CI status

.. |coverage| image:: https://coveralls.io/repos/github/jakelever/kindred/badge.svg?branch=master
   :target: https://coveralls.io/github/jakelever/kindred?branch=master
   :alt: Coverage status
   
.. |docs| image:: https://readthedocs.org/projects/kindred/badge/?version=stable
   :target: http://kindred.readthedocs.io/en/stable/
   :alt: Documentation status
   
.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT license

Kindred is a package for relation extraction in biomedical texts. Given some training data, it can build a model to identify relations between entities (e.g. drugs, genes, etc) in a sentence.

Installation
------------

You can install "kindred" via `pip`_ from `PyPI`_::

   $ pip install kindred

As of v2, Kindred relies on the `Spacy`_ toolkit for parsing. After installing kindred (which also installs spacy), you will need to install a Spacy language model. For instance, the command below installs the english language model::

   $ python -m spacy download en 

Usage
-----

Check out the `tutorial`_ that goes through a simple use case of extracting capital cities from text. More details and the full documentation can be found at `readthedocs`_.

BioNLP Shared Task Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> import kindred
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

Input Formats
~~~~~~~~~~~~~

Kindred can load several formats, including BioNLP Shared Task, JSON, BioC XML and a simple tag format. Check out the `file format documentation`_ for example data and code.

Citing
------
It would be wonderful if you could cite the `associated paper`_ for this package if used in any academic research.

.. code-block:: bibtex

   @article{lever2017painless,
      title={Painless {R}elation {E}xtraction with {K}indred},
      author={Lever, Jake and Jones, Steven},
      journal={BioNLP 2017},
      pages={176--183},
      year={2017}
   }

Contributing
------------
Contributions are very welcome.

License
-------

Distributed under the terms of the `MIT`_ license, "kindred" is free and open source software

Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`file an issue`: https://github.com/jakelever/kindred/issues
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
.. _`tutorial`: https://github.com/jakelever/kindred/tree/master/tutorial
.. _`readthedocs`: http://kindred.readthedocs.io/
.. _`Spacy`: https://spacy.io
.. _`associated paper`: http://aclweb.org/anthology/W17-2322
.. _`file format documentation`: https://kindred.readthedocs.io/en/stable/fileformats.html
