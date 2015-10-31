# sentimentAPI

```
Copyright (c) by respective owners. All rights reserved.  Released under license as described in the file LICENSE.txt
```

[![Build Status](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/badges/build.png?b=master)](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/build-status/master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/mikelynn2/sentimentAPI/?branch=master)


sentimentAPI is a python based text sentiment analysis api that you can use to test the positivity/negativity of a body of text.   You pass it text and get back a float score representing the sentiment of the text you passed in.  Scores equal to 0 and higher are positive, higher the score the more positive the statement.  Scores less than 0 are negative, lower the more negative.

## Features
- Simple JSON Based API
- Fast, around 1500/second on a single core machine.
- Trained on movie reviews - http://www.cs.cornell.edu/people/pabo/movie-review-data


```
# update repos
apt-get update

# install git
sudo apt-get -y install git

# install python stuff
sudo apt-get -y install python-dev python-pip libblas-dev liblapack-dev libatlas-base-dev gfortran

# move to your install dir
cd /opt

# pull code
git clone https://github.com/mikelynn2/sentimentAPI.git
```
