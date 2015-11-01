#!/usr/bin/python
'''

#start it up
gunicorn -c gunicornSettings.py sentimentAPI:app


# testing
ab -p example.json -T application/json -c 10 -n 2000 http://127.0.0.1:8000/api/sentiment/v1
curl -H "Content-Type: application/json" -X POST -d '{"text":"how is it going?"}' http://127.0.0.1:8000/api/sentiment/v1
curl -vX POST http://127.0.0.1:8000/api/sentiment/v1 -d @example.json --header "Content-Type: application/json"


'''

import sys
import falcon
import logging
import json
import os
import time
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm

#method for limiting request size
def max_body(limit):

	def hook(req, resp, resource, params):
		length = req.content_length
		if length is not None and length > limit:
			msg = ('The size of the request is too large. The body must not '
				'exceed ' + str(limit) + ' bytes in length.')

			raise falcon.HTTPRequestEntityTooLarge(
				'Request body is too large', msg)
	return hook


#Main Class
class SentimentAPI:

	testMode = True

	#startup method
	def __init__(self):
#self.logger = logging.getLogger('SentimentAPI.' + __name__)
#ch = logging.StreamHandler(sys.stdout)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#ch.setFormatter(formatter)
#self.logger.addHandler(ch)
#self.logger.info('training loaded')

		#train and build classifier
		self.classifier = self.train_classifier()
		self.logger('Training complete')

		#in test mode lets see how this is doing
		if self.testMode:
			self.score_classifier()


	#for logging program errors, not gunicron
	def logger(self, message):
		if(self.testMode):
			print("SentimentAPI %s\t%s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))
		else:
			with open('sentiment.log','a') as f:
				f.write("SentimentAPI %s\t%s" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))
				f.close()


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


#			analyzer=u'word',
#			binary=False,
#			decode_error=u'strict',
#			dtype=<type 'numpy.int64'>,
#			encoding=u'utf-8',
#			input=u'content',
#			lowercase=True,
#			max_df=1.0,
#			max_features=None,
#			min_df=1,
#			ngram_range=(1, 2),
#			norm=u'l2',
#			preprocessor=None,
#			smooth_idf=True

		train_vectors = self.vectorizer.fit_transform(train_data)

		# Perform classification with SVM, kernel=linear
		classifier_liblinear = svm.LinearSVC(
			loss='squared_hinge',
			max_iter=1000)
		classifier_liblinear.fit(train_vectors, train_labels)
		return classifier_liblinear

########different classifier
#		classifier_linear = svm.SVC(kernel='linear')
#		classifier_linear.fit(train_vectors, train_labels)
#		return classifier_linear


	#for testing the accuracy of the classifier
	def score_classifier(self):
		try:
			with open("testExamples.json", "r") as json_file:
				json_data = json.load(json_file)

			scoresRight = 0
			scoresWrong = 0
			for statement in json_data:
				result = self.test_classifier(statement["text"])
				#print result
				if result['result'] == statement["score"]:
					scoresRight+=1
					self.logger("[RIGHT] Text: %s\t\tActual: %s\tPredicted: %s" % (statement["text"], statement["score"], result['score']))
				else:
					self.logger("[WRONG] Text: %s\t\tActual: %s\tPredicted: %s" % (statement["text"], statement["score"], result['score']))
					scoresWrong+=1

			percentRight = (float(scoresRight)/(scoresRight+scoresWrong)) * 100
			self.logger("Scores: %d\tPercent Right: %1.2f\tRight: %d\tWrong: %d" % ((scoresRight+scoresWrong), percentRight, scoresRight, scoresWrong) )

		except Exception as ex:
			self.logger('Testing not completed')
			self.logger(repr(ex))


	###
	#Takes a string and returns dictionary object with 2 fields score/result 
	#result['score'] = .56
	#result['result'] = 'pos'
	###
	def test_classifier(self, words):
		test_data = [words]
		test_vectors = self.vectorizer.transform(test_data)
		#prediction_liblinear = self.classifier.predict(test_vectors)
		#print (str() + "\t" + prediction_liblinear[0])
		score = self.classifier.decision_function(test_vectors)
		score = score[0]
		if score >= 0:
			result = 'pos'
		else:
			result = 'neg'
		result = dict({'score':round(score,3),'result':result})
		return result


	###
	#Handles POST requests
	###
	@falcon.before(max_body(64 * 1024))
	def on_post(self, req, resp):
		try:
			text = req.context['doc']['text']
			resp.body = json.dumps(self.test_classifier(text))

		except Exception as ex:
			self.logger(repr(ex))

			raise falcon.HTTPServiceUnavailable(
				'Error',
				'Service error, try again later',
				30)

		resp.status = falcon.HTTP_200  # This is the default status
		resp.set_header('X-Powered-By', 'sentimentAPI')


class ErrorHandler(Exception):
	@staticmethod
	def handle(ex, req, resp, params):
		raise falcon.HTTPError(falcon.HTTP_725,
			'Error',
			repr(ex))

###
#forces t
###
class RequireJSON(object):

	def process_request(self, req, resp):
		if not req.client_accepts_json:
			raise falcon.HTTPNotAcceptable('This API only supports responses encoded as JSON.')


####
#early processor, makes sure the data we get from client is valid and json with all fields before sent to post accepter
####
class JSONTranslator(object):

	def process_request(self, req, resp):
		if req.content_length in (None, 0):
			# Nothing to do
			return

		body = req.stream.read()
		if not body:
			raise falcon.HTTPBadRequest('Empty request body',
				'A valid JSON document is required.')

		try:
			req.context['doc'] = json.loads(body.decode('utf-8'))

		except (ValueError, UnicodeDecodeError):
			raise falcon.HTTPError(falcon.HTTP_753,
				'Malformed JSON',
				'Could not decode the request body. The '
				'JSON was incorrect or not encoded as '
				'UTF-8.')

		#did they pass text var
		if 'text' not in req.context['doc']:
			raise falcon.HTTPBadRequest(
				'Error',
				'Missing json var text, come on you had one var to pass')

		#did they pass an empty text var
		if not req.context['doc']['text']:
			raise falcon.HTTPBadRequest(
				'Error',
				'Missing empty var text, come on you had one var to pass')

	def process_response(self, req, resp, resource):
		if 'result' not in req.context:
			return

		resp.body = json.dumps(req.context['result'])


# falcon.API instances are callable WSGI apps
app = falcon.API(middleware=[
	RequireJSON(),
	JSONTranslator(),
])

app.add_error_handler(ErrorHandler, ErrorHandler.handle)

# Resources are represented by long-lived class instances
sentimentAPI = SentimentAPI()

# things will handle all requests to the '/api/sentiment/v1' URL path
app.add_route('/api/sentiment/v1', sentimentAPI)



