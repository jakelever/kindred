# Kindred

<p>
<a href="https://pypi.python.org/pypi/kindred">
   <img src="https://img.shields.io/pypi/v/kindred.svg" />
</a>
<a href="https://travis-ci.org/jakelever/kindred">
   <img src="https://travis-ci.org/jakelever/kindred.svg?branch=master" />
</a>
<a href="https://coveralls.io/github/jakelever/kindred?branch=master">
   <img src="https://coveralls.io/repos/github/jakelever/kindred/badge.svg?branch=master" />
</a>
<a href="http://kindred.readthedocs.io/en/stable/">
   <img src="https://readthedocs.org/projects/kindred/badge/?version=stable" />
</a>
<a href="https://opensource.org/licenses/MIT">
   <img src="https://img.shields.io/badge/License-MIT-blue.svg" />
</a>
</p>

Kindred is a Python3 package for relation extraction in biomedical texts. Given some training data, it can build a model to identify relations between entities (e.g. drugs, genes, etc) in a sentence.

## Installation

You can install "kindred" via [pip](https://pypi.python.org/pypi/pip/) from [PyPI](https://pypi.org/project/kindred/)

```bash
pip install kindred
```

As of v2, Kindred relies on the [Spacy](https://spacy.io) toolkit for parsing. After installing kindred (which also installs spacy), you will need to install a Spacy language model. For instance, the command below installs the English language model::

```bash
python -m spacy download en
```

## Usage

Check out the [tutorial](https://github.com/jakelever/kindred/tree/master/tutorial) that goes through a simple use case of extracting capital cities from text. More details and the full documentation can be found at [readthedocs](http://kindred.readthedocs.io/).

### BioNLP Shared Task Example

```python
import kindred
trainCorpus = kindred.bionlpst.load('2016-BB3-event-train')
devCorpus = kindred.bionlpst.load('2016-BB3-event-dev')
predictionCorpus = devCorpus.clone()
predictionCorpus.removeRelations()
classifier = kindred.RelationClassifier()
classifier.train(trainCorpus)
classifier.predict(predictionCorpus)
f1score = kindred.evaluate(devCorpus, predictionCorpus, metric='f1score')
```

### PubAnnotation Example

```python
corpus = kindred.pubannotation.load('bionlp-st-gro-2013-development')
```

### PubTator Example

```python
corpus = kindred.pubtator.load([19894120,19894121])
```

### Input Formats

Kindred can load several formats, including BioNLP Shared Task, JSON, BioC XML and a simple tag format. Check out the [file format documentation](https://kindred.readthedocs.io/en/stable/fileformats.html) for example data and code.

### Citing

It would be wonderful if you could cite the [associated paper](http://aclweb.org/anthology/W17-2322) for this package if used in any academic research.

```bibtex
@article{lever2017painless,
   title={Painless {R}elation {E}xtraction with {K}indred},
   author={Lever, Jake and Jones, Steven},
   journal={BioNLP 2017},
   pages={176--183},
   year={2017}
}
```

## Contributing

Contributions are very welcome.

## License

Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT) license, "kindred" is free and open source software

## Issues

If you encounter any problems, please [file an issue](https://github.com/jakelever/kindred/issues) along with a detailed description.
