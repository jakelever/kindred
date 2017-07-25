
import numpy as np
from sklearn.linear_model import LogisticRegression

class LogisticRegressionWithThreshold:
	def __init__(self,threshold=0.5):
		#self.clf = svm.SVC(kernel='linear', class_weight='balanced', probability=True)
		self.clf = LogisticRegression(class_weight='balanced',random_state=1)
		self.threshold = threshold

	def fit(self,X,Y):
		self.clf.fit(X,Y)
		self.classes_ = self.clf.classes_

	def predict(self,X):
		probs = self.clf.predict_proba(X)

		# Ignore probabilities that fall below our threshold
		probs[probs<self.threshold] = -1.0

		# But make sure that the negative class (class=0) always has a slightly higher value
		probs[:,0][probs[:,0]<self.threshold] = -0.5

		# And get the highest probability for each row
		predictions = np.argmax(probs,axis=1)

		return predictions
		
