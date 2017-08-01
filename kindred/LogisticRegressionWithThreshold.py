
import numpy as np
from sklearn.linear_model import LogisticRegression

class LogisticRegressionWithThreshold:
	def __init__(self,threshold=0.5):
		"""
		Set up a Logistic Regression classifier that can use a different threshold for predictions and thereby be more lenient (lower threshold, false positives increase, false negatives decrease) or more conservative (higher threshold, false positives decrease, false negative increase).
		
		:param threshold: Threshold to use, should be between 0 and 1
		:type threshold: float
		"""

		self.clf = LogisticRegression(class_weight='balanced',random_state=1)
		self.threshold = threshold

	def fit(self,X,Y):
		"""
		Train the classifier using the associated matrix X and classes Y. Class zero should represent no associated class.
		
		:param X: Training vector
		:param Y: Associated class for each row of X
		:type X: sparse matrix
		:type Y: matrix
		"""

		self.clf.fit(X,Y)
		self.classes_ = self.clf.classes_

	def predict(self,X):
		"""
		Make predictions for the class of each row in X. Class zero should represent no prediction.
		
		:param X: Testing vector
		:type X: sparse matrix
		:return: Predictions of classes for each row in X
		:rtype: matrix
		"""

		probs = self.clf.predict_proba(X)

		# Ignore probabilities that fall below our threshold
		probs[probs<self.threshold] = -1.0

		# But make sure that the negative class (class=0) always has a slightly higher value
		probs[:,0][probs[:,0]<self.threshold] = -0.5

		# And get the highest probability for each row
		predictions = np.argmax(probs,axis=1)

		return predictions
		
