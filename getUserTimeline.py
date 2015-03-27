import json
import sys, os
from ConfigParser import SafeConfigParser
from twitter import *
from time import sleep
import logging
import math

def get_users(listfile):
    users = set()
    listfile = open(listfile,'r')
    
    for num, user in enumerate(listfile):
    	users.add(str(user.rstrip()))
    
    listfile.close()
    
    return users

def get_user_timelines(users, outfolder, api, user_id = "False"):
    print 'getting', len(users), 'user timelines'
    for user in users:
        n_tweets = 0
    	is_protected = "False"
    	try:
    	    if user_id == "True":
    	        user_info = api.users.show(user_id = user)
    	    else:
    		    user_info = api.users.show(screen_name = user)
    	    n_tweets = user_info['statuses_count']
    	    is_protected = str(user_info['protected'])
    	except TwitterHTTPError as e:
    		n_tweets = 0
    		logging.error(str(e))
    		if e.e.code == 401:
    		    print("Not Authorized - Check your Twitter settings.\n Exiting.")
    		    sys.exit()
    	if (is_protected == "True"):
    		logging.info("Oops, tweets for %s are protected. Moving on." % user)
    		continue
    	elif (n_tweets == 0):
    		logging.info("Oops, %s has no tweets or the account info is wrong. Moving on." % user)
    		continue
    	else:
    		logging.info("Getting %s tweets for %s. (Or ~3200, whichever is lower.)" % (n_tweets, user))
        n_loops = int(math.ceil(n_tweets/200.0))
    	if n_loops > 15:
    		n_loops = 15
    	try:
    		for i_loop in range(0, n_loops):
    			outfilename = ".".join([user,str(i_loop),'json'])
    			outfilename = "".join([outfolder,outfilename])
    			outfile = open(outfilename, 'a')
    			if user_id == "True":
    			    tweets = api.statuses.user_timeline(user_id = user, count = 200, page = i_loop+1)
    			else:
    			    tweets = api.statuses.user_timeline(screen_name = user, count = 200, page = i_loop+1)
    			if tweets:
    				outfile.write(json.dumps(tweets))
    			outfile.close()
    	except:
    		for i in sys.exc_info():
    			logging.warning(i)
    	# sleep(60)

# Main function
if __name__ == '__main__' :
    
    config = SafeConfigParser()
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, 'config/settings.cfg')
    config.read(config_file)
    
    logfile = config.get('files','logfile')
    listfile = config.get('files','listfile')
    outfolder = config.get('files','outfolder')
    
    user_id = config.get('options','user_id')
    
    logging.basicConfig(filename=logfile,level=logging.DEBUG)
    
    api = Twitter(api_version='1.1', auth=OAuth(config.get('twitter', 'access_token'),
                         config.get('twitter', 'access_token_secret'),
                         config.get('twitter', 'consumer_key'),
                         config.get('twitter', 'consumer_secret')))
    
    users = get_users(listfile)
    
    get_user_timelines(users, outfolder, api, user_id)
        
