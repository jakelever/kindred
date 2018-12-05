.. _fileformats:

File Formats
============

.. currentmodule:: kindred

Kindred can load several different file formats that contain text and their annotations. Below are examples of the different file formats with code for loading them.

BioNLP Shared Task format
-------------------------

This format, used in `BioNLP Shared Tasks <http://www.bionlp-st.org/>`_, is a standoff format. This means that the text is stored in one file and the annotations in other files. The text is stored in the .txt file, the entity annotations in the .a1 file and the relations in the .a2 file. For a project, you may have a directory with many .txt files, perhaps one per document or one per sentence. Then each file has its corresponding annotation files. If no relations annotations exist, the .a2 file may be missing.

Example file: example.txt

.. code-block:: none

   The colorectal cancer was caused by mutations in APC

Example file: example.a1

.. code-block:: none

   T1   disease 4 21    colorectal cancer
   T2   gene 49 52      APC

Example file: example.a2

.. code-block:: none

   E1   causes subj:T2 obj:T1

The .txt file contains Unicode text and no annotations. The .a1 file contains entity annotations. Each line is a new annotation and contains three tab-delimited columns. The first column is the unique identifier which is a T with a number. The second column contains the entity type, start and end position in the text with spaces in between. And the third column has a copy of the text for this entity. The .a2 file contains the relation annotations and contains tab-delimited columns. The first column is a unique identifier of the relation. The second column is the relation type and then the arguments of the relation, in the form of name:entityid. The entity identifier corresponds to the identifier in the .a1 file. Kindred supports relations with two or more arguments in the relation.

The identifiers for an entity annotation (in the .a1 file) must start with a T. The T stands for trigger. The identifiers for a relation annotation (in the .a2 file) must start with an E or R. For Kindred, these are synonymous. Note, that Kindred doesn't support "complex" relations, which are relations where one of the arguments is another relation. All relations must be between entities.

The following code would load these files to create a :class:`kindred.Document`.

.. code-block:: python

   doc = kindred.loadDoc(dataFormat='standoff',txtPath='example.txt',a1Path='example.a1',a2Path='example.a2')

Perhaps more useful, to load a whole corpus with multiple files in the format, use the following code assuming that the files are in the example directory. This will create a :class:`kindred.Corpus` object.

.. code-block:: python

   corpus = kindred.loadDir(dataFormat='standoff',directory='example/')

JSON format
-----------

This format, used by `PubAnnotation <http://pubannotation.org/>`_ and `PubTator <https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/>`_, stores the text and annotation data all together in a single file. Furthermore, multiple documents can be stored in a single document.

The format is standard JSON and is either a dictionary (for a single document) or a list of dictionaries (for multiple documents). Each dictionary needs to have three fields: text, denotations, and relations. The text is the text of the document. The denotations are the entity annotations and provide the unique identifier, entity type and location (span) in the text. The relations are the relation annotations. 

Example file: example.json

.. code-block:: json

   {
     "text": "The colorectal cancer was caused by mutations in APC",
     "denotations":
       [{"id":"T1", "obj":"disease",
         "span":{"begin":4,"end":21}},
        {"id":"T2", "obj":"gene",
         "span":{"begin":49,"end":52}}],
     "relations":
       [{"id":"R1","pred":"causes",
         "subj":"T2", "obj":"T1"}]
   }

To load a whole corpus with multiple files in the format, use the following code assuming that the files are in the example directory. This will create a :class:`kindred.Corpus` object.

.. code-block:: python

   corpus = kindred.loadDir(dataFormat='json',directory='example/')

BioC XML format
---------------

The BioC XML format contains text and annotations together in a single file. Furthermore, it is designed to store more than one document. It stores each document as "document" within a larger "collection". Each document contains passages (e.g. sections of a paper) which then contain the text, entity annotations, and relations. In loading this, each passage is turned into a single :class:`kindred.Document`. An example of the format is outlined below.

.. code-block:: xml

   <?xml version='1.0' encoding='UTF-8'?><!DOCTYPE collection SYSTEM 'BioC.dtd'>
   <collection>
     <source></source>
     <date></date>
     <key></key>
     <document>
       <id></id>
       <passage>
         <offset>0</offset>
         <text>The colorectal cancer was caused by mutations in APC</text>
         <annotation id="T1">
           <infon key="type">disease</infon>
           <location offset="4" length="17"/>
           <text>colorectal cancer</text>
         </annotation>
         <annotation id="T2">
           <infon key="type">gene</infon>
           <location offset="49" length="3"/>
           <text>APC</text>
         </annotation>
         <relation id="R1">
           <infon key="type">causes</infon>
           <node refid="T2" role="subj"/>
           <node refid="T1" role="obj"/>
         </relation>
       </passage>
     </document>
   </collection>

To load a whole directory of BioC XML files, use the code below. This will create a single :class:`kindred.Corpus` file with each passage found in all XML files in the directory turned a :class:`kindred.Document` entity.

.. code-block:: python

   corpus = kindred.loadDir(dataFormat='bioc',directory='example/')

Simple Tag format
-----------------

This format is not designed for production-use but for illustration and testing purposes. It is Kindred-specific. It is an XML-based format that keeps all annotations inline, to make it easier to see which entities are annotated. A relation tag provides a relation annotation and must have a type attribute. All other attributes are assumed to be relation argument. Any non-relation tag is assumed to be an entity annotation and must wrap around text. It must also have an id attribute.

Example file: example.simple

.. code-block:: xml

   The <disease id="T1">colorectal cancer</disease> was caused by mutations in <gene id="T2">APC</gene>
   <relation type="causes" subj="T2" obj="T1" />

It is most useful for quickly creating examples for testing. For example, the code below creates a :class:`kindred.Corpus` with a single document of the associated text and annotations.

.. code-block:: python

   text = '<drug id="1">Erlotinib</drug> is a common treatment for <cancer id="2">NSCLC</cancer>. <drug id="3">Aspirin</drug> is the main cause of <disease id="4">boneitis</disease>. <relation type="treats" subj="1" obj="2" />'

   corpus = :class:`kindred.Corpus`(text,loadFromSimpleTag=True)

If you do need to load a directory of these files (with suffix: .simple), the following command will load them into a :class:`kindred.Corpus` file.

.. code-block:: python

   corpus = kindred.loadDir(dataFormat='simpletag',directory='example/')

Streaming
---------

Some corpora are too large to load into memory in a single go. Kindred supports streaming in chunks of a corpus in the BioC format. The code below uses an iterator to load smaller :class:`kindred.Corpus` objects that contain a subset of the documents each time.

.. code-block:: python

   for corpus in kindred.iterLoadDataFromBioc('example.bioc.xml',corpusSizeCutoff=3):
           pass


