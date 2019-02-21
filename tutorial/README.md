# Tutorial

This tutorial will go through the steps needed to extract some relations from text. Kindred needs some example data for it to learn from and we'll show one option of how to get it. We have some example data that goes with this tutorial to show what's needed. The tutorial data set is a toy example of extracting capital cities from text describing cities around the world.
      
## Getting started

You'll need to install Kindred and the associated Spacy language pack. And you may want to download all the files in this directory so that you can work through this tutorial.

## Data
For successful relation extraction, you'll need three things: text, entities and annotated relations. We provide the first two for a the tutorial example and show how to get the third.

 - Text for extracting relations. This could be abstracts from PubMed, clinical notes or something completely different.
   - The corpus.txt file contains some sentences about cities of the world.
 - Names of entities (e.g. drug names, disease names)
   - city.txt contains a limited list of cities in the world
   - country.txt contains a limited list of countries
 - Annotated relations in text as examples for Kindred.
   - We're going to show how to create this

### What is annotated text?

Text can be annotated for entities (e.g. nouns) that identify terms of interest and then the relations between them. The example "files" below may provide an idea of how annotations work. The txt file contains the text, the a1 file contains the entity annotations and the a2 file contains the relation annotations.

onesentence.txt:
```
Glasgow is west of the the capital of Scotland, Edinburgh.
```

onesentence.a1
```
T1      city 0 7        Glasgow
T2      country 38 46   Scotland
T3      city 48 57      Edinburgh
```

onesentence.a2
```
R1      isCapital city:T3 country:T2
```

This is just one file format, but the principle is the same for all others. A stretch of text can be annotated as an entity, and relations can exist between entities. Kindred can only work with relations within a sentence and will ignore relations that cross sentence boundaries. You can find information about other file formats in the main documentation (link).

### Why do we need a list of entities?

Kindred needs to know what words to focus on. Whether it be a list of cities, drugs, or any concept, it needs to know which terms are important. It uses a basic exact-string matching approach to find terms. If you look in the city.txt and country.txt files, you will find a lists of entity names with one per line. Synonyms are separated by the pipe character ('|') as in the "United States of America|USA".
   
## Annotating data

Kindred needs examples of positive data (sentences with relations that you want to extract) and negative data (sentences without these relations). This will likely require annotating your own data for a specific problem, as not many datasets exist for annotated biomedical relations. Kindred provides a manuallyAnnotate method that identifies all the possible relations in a text and requests annotation of them.

The annotate.py script provides an implementation of this which we can use for the example data. Below we show a run of the annotate.py script with annotations of 10 sentences. Note that this is a very small set. Depending on the problem, you would likely want over a thousand sentences annotated.

<pre>
$ python annotate.py --corpus corpus.txt --wordlists city.txt,country.txt --outDir annotations
Setting up output directory
Loading and parsing corpus:
Splitting the corpus into sentences so that we can save any annotated sentences and don't need to annotate it all
Loading wordlists:
  city - city.txt
  country - country.txt
Annotating entities in corpus with wordlists
Finding all candidate relations
Time to through some of the candidate relations and annotate some...

For each sentence, choose an existing option or type the name of a new annotation

############################## (1/22)
<b>Paris</b> is the capital of <b>France</b>.
x:Done 0:None ? isCapital

############################## (2/22)
<b>Birmingham</b> is a city in the <b>United Kingdom</b>.
x:Done 0:None 1:isCapital ? 0

############################## (3/22)
The capital city of <b>Spain</b> is <b>Madrid</b>.
x:Done 0:None 1:isCapital ? 1

############################## (4/22)
<b>Los Angeles</b>, a large city in the <b>United States</b>, is home to Hollywood.
x:Done 0:None 1:isCapital ? 0

############################## (5/22)
<b>Canada</b>, a country with a population of 35 million, has its capital in <b>Ottawa</b>.
x:Done 0:None 1:isCapital ? 1

############################## (6/22)
<b>Glasgow</b> is the largest city in <b>Scotland</b>.
x:Done 0:None 1:isCapital ? 0

############################## (7/22)
We went to visit <b>Munich</b> in <b>Germany</b>.
x:Done 0:None 1:isCapital ? 0

############################## (8/22)
The capital of <b>Germany</b>, <b>Berlin</b>, has an unique history.
x:Done 0:None 1:isCapital ? 1

############################## (9/22)
<b>Edinburgh</b>, nicknamed the Athens of the North, is the capital of <b>Scotland</b> with many wonderful attractions.
x:Done 0:None 1:isCapital ? 1

############################## (10/22)
Edinburgh, nicknamed the <b>Athens</b> of the North, is the capital of <b>Scotland</b> with many wonderful attractions.
x:Done 0:None 1:isCapital ? 0

############################## (11/22)
<b>San Francisco</b> is one of the most visited cities in the <b>USA</b>.
x:Done 0:None 1:isCapital ? 0

############################## (12/22)
<b>Vancouver</b> is found in <b>Canada</b>'s western-most province, British Columbia.
x:Done 0:None 1:isCapital ? x

Saving annotated corpus of 10 sentences (with relations that you have just annotated)
Saving unannotated corpus of 8 sentences (which you did not review)
</pre>

The output of this run is a series of sentences with annotated relations and sentences without annotated relations (which were the ones we skipped) in the format outlined above. You can just download these (contained in the annotations.tar.gz file).

## Using the annotations

With annotated sentences, you can build a relation classifier and extract new relations. The buildAndUseClassifier.py example script will load the annotated sentences, build a classifier and predict relations on the sentences that we skipped. Usage is shown below.

```
python buildAndUseClassifier.py --dataToBuildModel annotations/annotated_relations/ --dataToApplyModel annotations/missing_relations/ --outDir predicted_relations
Loading corpora...
Building classifier...
Applying classifier...
Saving results to directory...

Predicted relations:
Delhi	India
Mombasa	Kenya
Nairobi	Kenya
Denver	Canada
```

As we gave it such a small training set, it obviously makes a few errors. Here, 2 of the 4 predictions are correct. Try annotating more or fewer of the sentences to begin with to see if it does better.

It also saves the predicted relations as annotations into the predicted_relations directory which may be useful for viewing the sentence that contains the annotation.

## Next Steps

So now you know the basics of creating a relation classifier. Obviously there are many more steps required to use it on your own dataset. So here are some ideas.

### Digging a little deeper

The provided example Kindred scripts show one option of creating and using an annotated dataset. The scripts are relatively short and the Kindred documentation should help you adjust them for your use-case. We'd suggest you look into the scripts and think what changes would suit your usecase better.

#### Your Text

Do you want to extract relations from clinical text, published articles or something else? You'll need to convert the data to a format that can be loaded into Python easily. If you're looking at published materials, the PubRunner project may be useful as it manages download of resources such as PubMed and data format conversion.

#### Your Entities

As with the country.txt and city.txt file, you need to provide Kindred with a list of names (and synonyms if wanted). If you are interested in drugs, you will need to provide a list of drug names. Some lists are available through the BioWordlists project. But you may need to create your own for your own interest.

### Tips, Tricks & Other Ideas

- When annotating your own dataset, you want to be creating an annotation set that isn't too imbalanced. You don't want your relation of interest to be incredibly rare within your dataset. If you find that only 10% of possible relations is of interest, then Kindred will have a hard time learning a good classifier. You can try to enrich for sentences by filtering for specific words. This would require you making some edits to the example Python scripts here.
- Another thought for annotation is that it is a good idea to have multiple (e.g. 3 or more) people annotate the same sentences and look to see if there is good agreement. The multiple datasets could then be merged through a majority vote system. If there is not good agreement, then the problem hasn't been well-defined and Kindred would have a very hard-time understanding what the human is trying to annotate. Improved agreement can be achieved through an annotation guide which explains how to annotate things, and simplifying the annotations to be done.
- The entity lists can have unique identifiers to make it easier to normalize terms (e.g. genes) back to an ontology (e.g. HUGO). Look into the loadWordlists function that is used in the tutorial Python scripts and the wordlists in the BioWordlists project.
- The [CancerMine](https://github.com/jakelever/cancermine) and [CIViCmine](https://github.com/jakelever/civicmine) projects are examples of large-scale information extraction that uses Kindred (alongside PubRunner) on PubMed and PubMed Central articles. These repositories could provide ideas for you.
- Try making a more conservative classifier. You could create a classifier using the [LogisticRegressionWithThreshold](https://kindred.readthedocs.io/en/stable/_autosummary/kindred.LogisticRegressionWithThreshold.html) class and set a higher threshold so that fewer false positives get through (but with more false negatives).
- You likely want to know how good your classifier is. The [evaluate](https://kindred.readthedocs.io/en/stable/_autosummary/kindred.evaluate.html) function will come in handy here. Annotate enough sentences and split them into a training and testing sets (using the [Corpus split](https://kindred.readthedocs.io/en/stable/_autosummary/kindred.Corpus.html#kindred.Corpus.split) function). Train a classifier on the training set, make predictions on the testing set (with relations removed using the [Corpus removeRelations](https://kindred.readthedocs.io/en/stable/_autosummary/kindred.Corpus.html#kindred.Corpus.removeRelations) function) and compare to the known annotations. Want to be really careful? Create a training, validation and testing sets. Read [this](https://doi.org/10.1038/nmeth.3945) for a bit more information.

