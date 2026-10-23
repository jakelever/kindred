# Release Notes

This is the temporary location for release notes for future releases of Kindred. Once the next release goes out, these will be migrated into the ReadTheDocs documentation. This is a holding place to keep track of significant changes.


## v2.8.4

- Fix regex-based variant (SNV) and microRNA detection in EntityRecognizer only finding matches in the first sentence of a document (token positions were document-relative but regex matches were sentence-relative)
- Fix compatibility with scikit-learn 1.8+, which removed the multi_class argument of LogisticRegression (the classifiers are all binary so results are unchanged)
- Test on Python 3.10-3.13 in GitHub Actions (Python 3.8 is no longer available)
- PubAnnotation loader uses HTTPS, sends a User-Agent and gives a clear error if the service does not return JSON
