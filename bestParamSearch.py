from sklearn.datasets import load_files
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

data = load_files('review_polarity/txt_sentoken')

vect = TfidfVectorizer()
X = vect.fit_transform(data.data)

params = { "tfidf__ngram_range": [(1, 1), (1, 2)],
	"tfidf__min_df": [3, 5, 8, 10],
	"tfidf__max_df": [.5, .8, 1.1, 1.2, 1.7, 1.9, 2.5],
	"svc__C": [.5, .6, .7, .8, .9, 1, 1, 1.1, 1.2, 1.3, 1.5, 2]
	}


clf = Pipeline([("tfidf", TfidfVectorizer(sublinear_tf=True)),
                ("svc", LinearSVC(loss='squared_hinge', max_iter=1000))])

gs = GridSearchCV(clf, params, verbose=2, n_jobs=-1)
gs.fit(data.data, data.target)
print(gs.best_estimator_)
print(gs.best_score_)

'''
[Parallel(n_jobs=-1)]: Done 2016 out of 2016 | elapsed: 59.5min finished
Pipeline(steps=[('tfidf', TfidfVectorizer(analyzer=u'word', binary=False, decode_error=u'strict',
        dtype=<type 'numpy.int64'>, encoding=u'utf-8', input=u'content',
        lowercase=True, max_df=1.1, max_features=None, min_df=8,
        ngram_range=(1, 2), norm=u'l2', preprocessor=None, smooth_idf=Tru...ax_iter=1000,
     multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
     verbose=0))])
0.886
'''