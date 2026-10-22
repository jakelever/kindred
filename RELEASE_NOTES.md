# Release Notes

This is the temporary location for release notes for future releases of Kindred. Once the next release goes out, these will be migrated into the ReadTheDocs documentation. This is a holding place to keep track of significant changes.


## v2.8.4

- Fix regex-based variant (SNV) and microRNA detection in EntityRecognizer only finding matches in the first sentence of a document (token positions were document-relative but regex matches were sentence-relative)
