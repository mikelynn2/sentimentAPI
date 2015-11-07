import sys
import logging
import json
import os
import time
import cPickle as pickle
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm


#Main Class
class Sentiment(object):

	testMode = True
	classifier = False
	pickleFileClassifier = 'classifier.p'
	pickleFileVectorizer = 'vectorizer.p'


	'''
	init/startup method
	'''
	def __init__(self, testMode = False):
##TODO: need to get the logging right, this isn't working.
#self.logger = logging.getLogger('SentimentAPI.' + __name__)
#ch = logging.StreamHandler(sys.stdout)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#self.logger.addHandler(ch)
#self.logger.info('training loaded')

		self.testMode = testMode

		# load up trained model
		self.load_trained()
		self.logger('Training complete')

		#in test mode lets see how this is doing
		if self.testMode:
			self.test_classifier()


	'''
	for logging program errors, not gunicron
	'''
	def logger(self, message):
		if(self.testMode):
			print("SentimentAPI %s\t%s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))
		else:
			with open('sentiment.log','a') as f:
				f.write("SentimentAPI %s\t%s\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))
				f.close()


	'''
	save trained model to pickle
	'''
	def save_trained(self):
		with open(self.pickleFileClassifier,'w') as f:
			pickle.dump(self.classifier, f, protocol=2)

		with open(self.pickleFileVectorizer,'w') as f:
			pickle.dump(self.vectorizer, f, protocol=2)
		return True

	'''
	load trained model to pickle
	'''
	def load_trained(self):
		if self.testMode == False:
			if os.path.isfile(self.pickleFileClassifier) and os.path.isfile(self.pickleFileVectorizer):
				with open(self.pickleFileClassifier,'r') as f:
					self.classifier = pickle.load(f)
				with open(self.pickleFileVectorizer,'r') as f:
					self.vectorizer = pickle.load(f)
					return True

		self.train_classifier()


	'''
	trains classifier and saves
	'''
	def train_classifier(self):

		classes = ['pos', 'neg']

		# Read the data
		train_data = []
		train_labels = []
		test_data = []
		for curr_class in classes:
			dirname = os.path.join('review_polarity/txt_sentoken', curr_class)
			for fname in os.listdir(dirname):
				with open(os.path.join(dirname, fname), 'r') as f:
					content = f.read()
					train_data.append(content)
					train_labels.append(curr_class)

		# Create feature vectors
		self.vectorizer = TfidfVectorizer(
			min_df = 8,
			max_df = 1.9,
			stop_words = 'english',
			sublinear_tf = True,
			ngram_range=(1, 2),
			use_idf = True
			)

		train_vectors = self.vectorizer.fit_transform(train_data)

		if self.testMode:
			from sklearn.cross_validation import train_test_split

			train_vectors, train_vectors_valid, train_labels, train_labels_valid = train_test_split(
				train_vectors, train_labels, test_size=0.10)

		# Perform classification
		self.classifier = svm.LinearSVC(
			C=.5,
			loss='squared_hinge',
			max_iter=1000,
			multi_class='ovr',
			random_state=None,
			penalty='l2',
			tol=0.0001
			)

		self.classifier.fit(train_vectors, train_labels)

		if self.testMode:
			from sklearn.metrics import accuracy_score
			prediction = self.classifier.predict(train_vectors_valid)
			self.logger("Accuracy Score: {0}%".format(accuracy_score(train_labels_valid, prediction) * 100) )

		# save out
		self.save_trained()



	'''
	self testing method
	looks at custom examples in testExamples.json and produces
	some data about how right/wrong we were
	'''
	def test_classifier(self):
		try:
			with open("testExamples.json", "r") as json_file:
				json_data = json.load(json_file)

			scoresRight = 0
			scoresWrong = 0
			for statement in json_data:
				result = self.classify(statement["text"])
				if result['result'] == statement["score"]:
					scoresRight+=1
					self.logger("[RIGHT] Text: %s\t\tActual: %s\tPredicted: %s" % 
						(statement["text"], statement["score"], result['score']))

				else:
					scoresWrong+=1
					self.logger("[WRONG] Text: %s\t\tActual: %s\tPredicted: %s" % 
						(statement["text"], statement["score"], result['score']))
				
			percentRight = (float(scoresRight)/(scoresRight+scoresWrong)) * 100
			self.logger("Scores: %d\tPercent Right: %1.2f\tRight: %d\tWrong: %d" %
				((scoresRight+scoresWrong), percentRight, scoresRight, scoresWrong) )

		except Exception as ex:
			self.logger('Model not loaded, try again')
			self.logger(repr(ex))


	'''
	Takes a string and returns dictionary object with 2 fields score/result
	result['score'] = .56
	result['result'] = 'pos'
	'''
	def classify(self, words):
		test_data = [words]
		test_vectors = self.vectorizer.transform(test_data)
		score = self.classifier.decision_function(test_vectors)
		score = score[0]
		if score >= 0:
			result = 'pos'
		else:
			result = 'neg'
		result = dict({'score':round(score,3),'result':result})
		return result



