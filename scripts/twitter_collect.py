import io
import json
import sys, os
from ConfigParser import SafeConfigParser
from twitter import *
from time import sleep
import math

# get list of user_ids or screen_names to fetch
def get_users(listfile):
    users = set()
    
    # get the list from the file we specified
    listfile = open(listfile,'r')
    
    # add each line to the users set
    for num, user in enumerate(listfile):
    	users.add(str(user.rstrip()))

    listfile.close() # clean up
    
    return users # a set of user_ids or screen_names

# query Twitter API by user_id or screen_name and dump results to JSON file
def get_user_timelines(users, outfolder, api, user_id = "False"):
    print("Getting %s user timeline(s). Storing files in %s." % (str(len(users)), outfolder))
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
            if e.e.code == 401 or e.e.code == 400: # Not authorized
                print("Not Authorized - Check your Twitter settings.\n Exiting.")
                print(str(e))
                sys.exit()
            elif e.e.code == 404: # Not found
                print("Oops, %s has no tweets or the account info is wrong. Moving on." % user)
                continue
        # logged in ok and found the user
        if is_protected == "True": # Users' tweets are protected, account is private
            print("Oops, tweets for %s are protected. Moving on." % user)
            continue
        elif n_tweets == 0: # User has no tweets
            print("%s has no tweets to get. Moving on." % user)
            continue
        else: # Account is public, one or more tweets to collect
            print("Getting %s tweets for %s. (Or ~3200, whichever is lower.)" % (n_tweets, user))
            n_loops = int(math.ceil(n_tweets/200.0)) # Twitter lets us get 200 at a time, max 3200
        if n_loops > 15:
            n_loops = 15
        try: # make a JSON file named user.page_number.json and put it in the folder we specified

            for i_loop in range(0, n_loops):
                outfilename = ".".join([user,str(i_loop),'json'])
                outfilename = "".join([outfolder,outfilename])
                outfile = io.open(outfilename, mode='wt', encoding='utf8')
                try:
                    if user_id == "True": # if we're searching by user_id
                        tweets = api.statuses.user_timeline(user_id = user, count = 200, page = i_loop+1)
                    else: # if we're searching by screen_name or handle
                        tweets = api.statuses.user_timeline(screen_name = user, count = 200, page = i_loop+1)
                except TwitterHTTPError as e:
                    if e.e.code == 429: # Rate limit exceeded
                        print("Rate limit exceeded. Sleeping for 15 minutes.")
                        sleep(60 * 15)
                if tweets: # we got tweets, lets dump 'em to JSON
                    outfile.write(json.dumps(tweets,ensure_ascii=False, encoding='utf8'))
                    outfile.write(u'\n')
                    outfile.flush()
                outfile.close() # clean up
            print("Done collecting.")
        except: # something went wrong, could be that Twitter's down, log it and we'll look later
            for i in sys.exc_info():
                print(i)

# Main function
if __name__ == '__main__' :

    config = SafeConfigParser()
    script_dir = os.path.dirname(__file__)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, '../settings.cfg')
    config.read(config_file)
    
    # tell script where to put the JSON files returned
    listfile = config.get('files','listfile')
    outfolder = config.get('files','outfolder')
    
    # should we search by user_id? default is no, use screen_name/handle
    user_id = config.get('options','user_id')
        
    # connect to the API using OAuth credentials
    api = Twitter(api_version='1.1', auth=OAuth(config.get('twitter', 'access_token'),
       config.get('twitter', 'access_token_secret'),
       config.get('twitter', 'consumer_key'),
       config.get('twitter', 'consumer_secret')))
    
    # find out who we're searching for
    users = get_users(listfile)
    
    # go get their tweets
    get_user_timelines(users, outfolder, api, user_id)

sys.exit()

