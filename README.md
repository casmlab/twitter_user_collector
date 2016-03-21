user-timeline-tools
======================
(v.3 - March 27, 2015)

user-timeline-tools are a set of Python scripts that get UserTimeline data from Twitter and parse it into a MySQL database so that a Django app can serve it up. If you just want to collect "raw" JSON, you can use just [getUserTimeline.py]() and skip the parsing.

Python Versions
---------------
```user-timeline-tools``` was written for Python 2.7. It has not been tested on other versions.

Other Requirements
------------------
**Option 1**: If you're using [Anaconda](https://www.continuum.io/downloads) to manage your python environments and packages, you can recreate our python environment from the provided `environment.yml` file: `conda env create -n name-of-environment -f environment.yml`. To switch to your newly created environment, `source activate name-of-environment`.

**Option 2**: Alternatively, you can install the requirements for user-timeline-tools using pip: `pip install -r requirements.txt`.

What You Need Before you Start
------------------------------
You need a list of Twitter screen_names or user_ids stored in a plain text file, one name per line. You can use screen_names OR ids but not both in the same file. 

You also need [OAuth credentials from Twitter.](https://dev.twitter.com/oauth/overview) 

Tell the script where to store data using [config/settings_example.cfg](config/settings_example.cfg). Remember to save that file as ```settings.cfg``` once you've entered your settings.

Setup and Go
------------
If you just want to get the tweets into JSON files:

1. Create a ```settings.cfg``` that looks like [config/settings_example.cfg](config/settings_example.cfg) but with your values
2. Run [getUserTimeline.py](getUserTimeline.py) (will take a while, maybe even days)

	Once you have the tweets, if you want to parse into a Django-ready DB:

3. Create a MySQL database using [config/schema.sql](config/schema.sql)
4. Run [parseUserTimeline.py](parseUserTimeline.py) (will take a while, maybe even a day)

