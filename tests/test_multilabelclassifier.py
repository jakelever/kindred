import kindred
import random
import numpy as np
import sklearn

def test_multilabelclassifier():
	np.random.seed(1)

	N = 1000
	split = N // 2
	X = np.random.rand(N,2)

	Ya = [ 1 if X[i,0] < 0.5 else 0 for i in range(X.shape[0]) ]
	Yb = [ 1 if X[i,1] < 0.5 else 0 for i in range(X.shape[0]) ]

	Y = np.column_stack((Ya,Yb))

	Xtrain = X[:split,:]
	Ytrain = Y[:split,:]

	Xtest = X[split:,:]
	Ytest = Y[split:,:]

	classifier = kindred.MultiLabelClassifier(sklearn.linear_model.LogisticRegression,random_state=1,solver='lbfgs')

	classifier.fit(Xtrain,Ytrain)

	predicted = classifier.predict(Xtest)
	assert predicted.shape == Ytest.shape
	rmse = np.sqrt(np.mean((predicted-Ytest)**2))
	assert rmse == 0.07071067811865475

	probs = classifier.predict_proba(Xtest)
	assert probs.shape == Ytest.shape
	rmse_probs = np.sqrt(np.mean((probs-Ytest)**2))
	assert rmse_probs == 0.20186752465655197


