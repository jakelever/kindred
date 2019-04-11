import sklearn
import numpy as np
import inspect

class MultiLabelClassifier:
	"""
	Wrapper for a set of classifiers that can behave as a multi-label classifier. Multi-label means that each data point can have multiple labels (or belong to multiple classes). This is particularly relevant in text mining where two words can belong to multiple relations. This class just creates a classifier for each label and runs then together, concatenating the results into a nice matrix form
	"""
	def __init__(self,classifier,**kwargs):
		"""
		Create a classifier that can handle multiple labels using multiple instance of the supplied classifier class. Any additional parameters are passed onto the classifier.

		:param classifier: The type of classifier to use
		:type classifier: class with fit/predict
		"""

		assert inspect.isclass(classifier), "Must provide a class with fit/predict methods"

		assert hasattr(classifier, 'fit') and callable(getattr(classifier, 'fit')), "Provided classifier class must have a fit method"
		assert hasattr(classifier, 'predict') and callable(getattr(classifier, 'predict')), "Provided classifier class must have a predict method"

		self.classifierClass = classifier
		self.classifierArgs = kwargs

		self.classifiers = None
		self.labelCount = None
		self.fitted = False

	def fit(self,X,Y):
		"""
		Fit multiple classifiers for the number of labels provided

		:param X: Training matrix (with n_samples rows and n_features columns)
		:param Y: Target matrix (with n_samples rows and n_labels columns)
		:type X: matrix
		:type Y: matrix
		"""
		assert not self.fitted, "Cannot refit classifier"
		assert X.shape[0] == Y.shape[0], "The numbers of rows of X and Y should be the number of samples (and so the same)"

		self.labelCount = Y.shape[1]
		self.classifiers = [ self.classifierClass(**self.classifierArgs) for _ in range(self.labelCount) ]
		for l in range(self.labelCount):
			assert Y[:,l].min()==0, "Column %d of Y must contain negative data (class=0)"
			assert Y[:,l].max()==1, "Column %d of Y must only contain a single class (0 or 1)"

			self.classifiers[l].fit(X,Y[:,l])

		self.fitted = True

	def predict(self,X):
		"""
		Predict for multiple labels and return a matrix with predicted labels

		:param X: Testing matrix (with n_samples rows and n_features columns)
		:type X: matrix
		:return: Predicted binary matrix (with n_samples rows and n_labels columns)
		:rtype: matrix
		"""
		assert self.fitted, "Classifier has not been fit"
		
		predictions = [ self.classifiers[l].predict(X) for l in range(self.labelCount) ]

		return np.column_stack(predictions)
	

	def has_predict_proba(self):
		"""
		Returns whether the underlying classifier has the predict_proba method

		:return: Whether classifier has predict_proba method
		:rtype: bool
		"""

		return hasattr(self.classifierClass, 'predict_proba') and callable(getattr(self.classifierClass, 'predict_proba'))

	def predict_proba(self,X):
		"""
		Predict for multiple labels and return a matrix with predicted labels. Returns for the probability for the positive class (for each label column) only.

		:param X: Testing matrix (with n_samples rows and n_features columns)
		:type X: matrix
		:return: Predicted probability matrix (with n_samples rows and n_labels columns)
		:rtype: matrix
		"""
		assert self.has_predict_proba(), "Provided classifier class must have a predict_proba method"
		assert self.fitted, "Classifier has not been fit"
		
		predictions = [ self.classifiers[l].predict_proba(X)[:,1] for l in range(self.labelCount) ]

		return np.column_stack(predictions)

