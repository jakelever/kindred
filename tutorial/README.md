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
Glasgow is west of the the capital of Scotland, Edinburgh.

onesentence.a1

onesentence.a2

This is just one file format, but the principle is the same for all others. A stretch of text can be annotated as an entity, and relations can exist between entities. Kindred can only work with relations within a sentence and will ignore relations that cross sentence boundaries. You can find information about other file formats in the main documentation (link).

### Why do we need a list of entities?

Kindred needs to know what words to focus on. Whether it be a list of cities, drugs, or any concept, it needs to know which terms are important. It uses a basic exact-string matching approach to find terms. If you look in the city.txt and country.txt files, you will find a lists of entity names with one per line. Synonyms are separated by the pipe character ('|') as in the "United States of America|USA".
   
## Annotating data

Kindred needs examples of positive data (sentences with relations that you want to extract) and negative data (sentences without these relations). This will likely require annotating your own data for a specific problem, as not many datasets exist for annotated biomedical relations. Kindred provides a manuallyAnnotate method that identifies all the possible relations in a text and requests annotation of them.

The annotate.py script provides an implementation of this which we can use for the example data. Below we show a run of the annotate.py script with annotations of 10 sentences. Note that this is a very small set. Depending on the problem, you would likely want over a thousand sentences annotated.

```
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
Paris is the capital of France.
x:Done 0:None ? isCapital

############################## (2/22)
Birmingham is a city in the United Kingdom.
x:Done 0:None 1:isCapital ? 0

############################## (3/22)
The capital city of Spain is Madrid.
x:Done 0:None 1:isCapital ? 1

############################## (4/22)
Los Angeles, a large city in the United States, is home to Hollywood.
x:Done 0:None 1:isCapital ? 0

############################## (5/22)
Canada, a country with a population of 35 million, has its capital in Ottawa.
x:Done 0:None 1:isCapital ? 1

############################## (6/22)
Glasgow is the largest city in Scotland.
x:Done 0:None 1:isCapital ? 0

############################## (7/22)
We went to visit Munich in Germany.
x:Done 0:None 1:isCapital ? 0

############################## (8/22)
The capital of Germany, Berlin, has an unique history.
x:Done 0:None 1:isCapital ? 1

############################## (9/22)
Edinburgh, nicknamed the Athens of the North, is the capital of Scotland with many wonderful attractions.
x:Done 0:None 1:isCapital ? 1

############################## (10/22)
Edinburgh, nicknamed the Athens of the North, is the capital of Scotland with many wonderful attractions.
x:Done 0:None 1:isCapital ? 0

############################## (11/22)
San Francisco is one of the most visited cities in the USA.
x:Done 0:None 1:isCapital ? x
Saving annotated corpus of 9 sentences (with relations that you have just annotated)
Saving unannotated corpus of 9 sentences (which you did not review)
```

The output of this run is a series of annotated sentences and unannotated sentences in the format outlined above. You can just download these (contained in the annotations.tar.gz file).

## Using the annotations

With annotated sentences, you can build a relation classifier and extract new relations. The classifySentences.py example script will load the annotated sentences, build a classifier and predict relations on the unannotated sentences. Usage is shown below.

TODO

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
- The CancerMine and CIViCmine projects are examples of large-scale information extraction that uses Kindred (alongside PubRunner) on PubMed and PubMed Central articles. These repositories could provide ideas for you.
