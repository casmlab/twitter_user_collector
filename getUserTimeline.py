import json
import sys
from twitter import *
from time import sleep
import logging
import math

# CHECK THESE SETTINGS FIRST
logfile = "FULL PATH TO FILE" # where should the script log its progress and warnings
listfile = open('FULL PATH TO FILE','r') # list of users to collect, one screen_name per line
outfilepath = "FULL PATH TO FOLDER - INCLUDE TRAILING SLASH" # where should the script save its results
api = Twitter(api_version='1.1', auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET)) # your Twitter OAuth credentials

# helper functions
def intOnly(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

logging.basicConfig(filename=logfile,level=logging.DEBUG)

for count, name in enumerate(listfile):
	name = str(name.rstrip())
	n_tweets = 0
	is_protected = "False"
	try:
		user_info = api.users.show(screen_name = name)
		n_tweets = user_info['statuses_count']
		is_protected = str(user_info['protected'])
	except TwitterHTTPError as e:
		n_tweets = 0
		logging.info(str(e))
	if (is_protected == "True"):
		logging.info("Oops, tweets for %s are protected. Moving on." % name)
		continue
	elif (n_tweets == 0):
		logging.info("Oops, %s has no tweets or the account info is wrong. Moving on." % name)
		continue
	else:
		logging.info("Getting %s tweets for %s. (Or ~3200, whichever is lower.)" % (n_tweets, name))
	n_loops = int(math.ceil(n_tweets/200.0))
	if n_loops > 15:
		n_loops = 15
	try:
		for i_loop in range(0, n_loops):
			outfilename = ".".join([name,str(i_loop),'json'])
			outfilename = "".join([outfilepath,outfilename])
			outfile = open(outfilename, 'a')
			tweets = api.statuses.user_timeline(screen_name = name, count = 200, page = i_loop+1)
			if tweets:
				outfile.write(json.dumps(tweets))
			outfile.close()
	except:
		for i in sys.exc_info():
			logging.warning(i)
	sleep(60)

listfile.close()
