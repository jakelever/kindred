import os
import codecs
import json
import csv
import kindred
import bioc
import six


def convertKindredCorpusToBioCCollection(corpus):
    assert isinstance(corpus, kindred.Corpus)
    collection = bioc.BioCCollection()
    for kdoc in corpus.documents:
        assert isinstance(kdoc, kindred.Document)

        biocDoc = bioc.BioCDocument()
        collection.add_document(biocDoc)

        if 'id' in kdoc.metadata:
            biocDoc.id = kdoc.metadata['id']
        biocDoc.infons = kdoc.metadata

        passage = bioc.BioCPassage()
        passage.text = kdoc.text
        passage.offset = 0
        biocDoc.add_passage(passage)

        seenEntityIDs = set()
        kindredID2BiocID = {}
        for e in kdoc.entities:
            assert isinstance(e, kindred.Entity)

            a = bioc.BioCAnnotation()
            a.text = e.text
            a.infons = {'type': e.entityType}
            a.infons.update(e.metadata)

            if e.sourceEntityID is None:
                a.id = str(e.entityID)
            else:
                a.id = str(e.sourceEntityID)

            assert not a.id in seenEntityIDs, "Multiple entities with the same ID (%s) found" % a.id
            seenEntityIDs.add(a.id)
            kindredID2BiocID[e.entityID] = a.id

            for start, end in e.position:
                l = bioc.BioCLocation(offset=start, length=(end - start))
                a.locations.append(l)

            passage.annotations.append(a)

        for r in kdoc.relations:
            assert isinstance(r, kindred.Relation)
            biocR = bioc.BioCRelation()
            biocR.infons = {'type': r.relationType}

            entitiesInRelation = r.entities
            argNames = r.argNames
            if argNames is None:
                argNames = ["arg%d" % i for i, _ in enumerate(entitiesInRelation)]

            for argName, entity in zip(argNames, entitiesInRelation):
                node = bioc.BioCNode(role=argName, refid=kindredID2BiocID[entity.entityID])
                biocR.nodes.append(node)

            passage.relations.append(biocR)

    return collection


def getUniqueRelationID(relations):
    usedIDs


def saveDocToSTFormat(doc, txtPath, a1Path, a2Path):
    assert isinstance(doc, kindred.Document)

    with codecs.open(txtPath, 'w', 'utf8') as txtFile, codecs.open(a1Path, 'w', 'utf8') as a1File, codecs.open(a2Path,
                                                                                                               'w',
                                                                                                               'utf8') as a2File:
        txtFile.write(doc.text)

        for e in doc.entities:
            assert isinstance(e, kindred.Entity)
            assert isinstance(e.sourceEntityID,
                              six.string_types), "Entities must have a sourceEntityID (e.g. T1) to be saved in the standoff format"

            positions = ";".join("%d %d" % (start, end) for start, end in e.position)
            line = "%s\t%s %s\t%s" % (e.sourceEntityID, e.entityType, positions, e.text)
            a1File.write(line + "\n")

        relationsHaveSourceIDs = [not (r.sourceRelationID is None) for r in doc.relations]
        assert all(relationsHaveSourceIDs) or not any(
            relationsHaveSourceIDs), "All relations must have sourceRelationID or none can have them."

        useSourceRelationIDs = all(relationsHaveSourceIDs)

        for i, r in enumerate(doc.relations):
            assert isinstance(r, kindred.Relation)

            relationType = r.relationType
            relationEntityIDs = [entity.sourceEntityID for entity in r.entities]

            if r.argNames is None:
                argNames = [("arg%d" % (argI + 1)) for argI in range(len(relationEntityIDs))]
            else:
                argNames = r.argNames

            arguments = " ".join(["%s:%s" % (a, b) for a, b in zip(argNames, relationEntityIDs)])

            if useSourceRelationIDs:
                relationID = str(r.sourceRelationID)
            else:
                relationID = "R%d" % (i + 1)

            line = "%s\t%s %s" % (relationID, relationType, arguments)
            a2File.write(line + "\n")


def saveCorpusToPubAnnotationFormat(corpus, path):
    assert isinstance(corpus, kindred.Corpus)

    pubannotated = []
    for doc in corpus.documents:
        p = {}
        p['text'] = doc.text
        p['denotations'] = []
        p['relations'] = []

        for e in doc.entities:
            spans = [{'begin': pos[0], 'end': pos[1]} for pos in e.position]
            if len(spans) == 1:
                spans = spans[0]
            p['denotations'].append({'id': e.sourceEntityID, 'span': spans, 'obj': e.entityType})

        relationsHaveSourceIDs = [not (r.sourceRelationID is None) for r in doc.relations]
        assert all(relationsHaveSourceIDs) or not any(
            relationsHaveSourceIDs), "All relations must have sourceRelationID or none can have them."

        useSourceRelationIDs = all(relationsHaveSourceIDs)

        for i, r in enumerate(doc.relations):
            assert len(r.entities) == 2, "PubAnnotation only supports binary relations"
            eID0 = r.entities[0].sourceEntityID
            eID1 = r.entities[1].sourceEntityID

            if useSourceRelationIDs:
                relationID = str(r.sourceRelationID)
            else:
                relationID = "R%d" % (i + 1)

            p['relations'].append({'id': relationID, 'subj': eID0, 'pred': r.relationType, 'obj': eID1})

        pubannotated.append(p)

    with open(path, 'w') as outF:
        json.dump(pubannotated, outF, indent=2)


def saveCorpusToCSVFormat(corpus, path):
    assert isinstance(corpus, kindred.Corpus)

    csv_annotations = []
    for doc in corpus.documents:
        entities = {}
        for e in doc.entities:
            spans = [{'begin': pos[0], 'end': pos[1]} for pos in e.position]
            entities[e.sourceEntityID] = {'span': spans, 'ent_text': e.text, 'ent_type': e.entityType}
        relationsHaveSourceIDs = [not (r.sourceRelationID is None) for r in doc.relations]
        assert all(relationsHaveSourceIDs) or not any(
            relationsHaveSourceIDs), "All relations must have sourceRelationID or none can have them."
        useSourceRelationIDs = all(relationsHaveSourceIDs)
        for i, r in enumerate(doc.relations):
            annotation = {}
            if useSourceRelationIDs:
                relationID = str(r.sourceRelationID)
            else:
                relationID = "R%d" % (i + 1)
            annotation['documentName'] = doc.sourceFilename
            annotation['text'] = doc.text
            annotation['relationID'] = relationID
            annotation['relationType'] = r.relationType
            annotation['entitySubject'] = entities[r.entities[0].sourceEntityID]['ent_text']
            annotation['entitySubject_Type'] = entities[r.entities[0].sourceEntityID]['ent_type']
            annotation['entitySubject_Pos'] = entities[r.entities[0].sourceEntityID]['span']
            annotation['entityObject'] = entities[r.entities[1].sourceEntityID]['ent_text']
            annotation['entityObject_Type'] = entities[r.entities[1].sourceEntityID]['ent_type']
            annotation['entityObject_Pos'] = entities[r.entities[1].sourceEntityID]['span']
            csv_annotations.append(annotation)
    if csv_annotations:
        keys = csv_annotations[0].keys()
    with open(path, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(csv_annotations)


def save(corpus, dataFormat, path):
    """
    Save a corpus to a directory

    :param corpus: The corpus of documents to save
    :param dataFormat: Format of data to save (only 'standoff', 'biocxml', 'pubannotation' and 'csv' are supported currently)
    :param path: Path where corpus should be saved. Must be an existing directory for 'standoff'.
    :type corpus: kindred.Corpus
    :type dataFormat: str
    :type path: str
    """

    assert dataFormat in ['standoff', 'biocxml', 'pubannotation', 'csv']

    assert isinstance(corpus, kindred.Corpus)

    if dataFormat == 'standoff':
        assert os.path.isdir(path), "Path must be an existing directory"

        for i, d in enumerate(corpus.documents):
            if d.sourceFilename is None:
                base = "%08d" % i
            else:
                base = d.sourceFilename

            txtPath = os.path.join(path, '%s.txt' % base)
            a1Path = os.path.join(path, '%s.a1' % base)
            a2Path = os.path.join(path, '%s.a2' % base)

            saveDocToSTFormat(d, txtPath, a1Path, a2Path)
    elif dataFormat == 'biocxml':
        assert not os.path.isdir(path), "Path cannot be an existing directory for 'biocxml'."

        collection = convertKindredCorpusToBioCCollection(corpus)
        with bioc.biocxml.iterwrite(path) as writer:
            for doc in collection.documents:
                writer.write_document(doc)
    elif dataFormat == 'pubannotation':
        assert not os.path.isdir(path), "Path cannot be an existing directory for 'pubannotation'."

        saveCorpusToPubAnnotationFormat(corpus, path)
    elif dataFormat == 'csv':
        assert not os.path.isdir(path), "Path cannot be an existing directory for 'csv'."

        saveCorpusToCSVFormat(corpus, path)


