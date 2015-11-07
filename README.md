# sentimentAPI
```
Copyright (c) by respective owners. All rights reserved.  Released under license as described in the file LICENSE.txt
```
sentimentAPI is a python based text sentiment analysis api that you can use to test the positivity/negativity of a body of text.   You pass it text and get back a float score representing the sentiment of the text you passed in.  Scores equal to 0 and higher are positive, higher the score the more positive the statement.  Scores less than 0 are negative, lower the more negative.

[![Build Status](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/badges/build.png?b=master)](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/build-status/master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/?branch=master)


## Features
- Simple JSON Based API
- Fast, around 1500/second on a single core machine.
- Trained on movie reviews - http://www.cs.cornell.edu/people/pabo/movie-review-data

## Important
- Memory required to compile scipy is around 2-3G.  Make sure you have at least that.


## Install
```
# update repos
sudo apt-get -y update

# install git
sudo apt-get -y install git

# install python and stuff python needs to compile packages
sudo apt-get -y install python-dev python-pip libblas-dev liblapack-dev libatlas-base-dev gfortran

# install python requirements
export LC_ALL=C
sudo pip install -U setuptools
sudo pip install -U numpy scipy scikit-learn sklearn cython falcon gunicorn gevent

# move to your install dir
cd /opt

# pull code
git clone https://github.com/mikelynn2/sentimentAPI.git

# start it up
cd /opt/sentimentAPI
gunicorn -c gunicornSettings.py sentimentAPI:app

# simple test
curl -H "Content-Type: application/json" -X POST -d '{"text":"how is it going?"}' http://127.0.0.1:8000/api/sentiment/v1

# file json test
curl -vX POST http://127.0.0.1:8000/api/sentiment/v1 -d @example.json --header "Content-Type: application/json"

# load test
ab -p example.json -T application/json -c 10 -n 2000 http://127.0.0.1:8000/api/sentiment/v1

```

## Settings
All settings are located in gunicornSettings.py.  They mostly deal with the API serving
