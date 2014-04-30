import argparse, collections, fnmatch, json, math, mysql.connector as sql, os, requests, sys, time
from ConfigParser import SafeConfigParser
from datetime import datetime
from mysql.connector import errorcode
from requests import HTTPError
from requests import ConnectionError

def printUTF8(info) :
    print(info.encode('ascii', 'replace').decode())

def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

# Connect to MySQL using config entries
def connect() :
    config = SafeConfigParser()
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, 'config/settings.cfg')
    config.read(config_file)
    sections = config.sections(); sections.remove("MySQL")
    db_params = {
            'user' : config.get("MySQL","user"),
            'password' : config.get("MySQL","password"),
            'host' : config.get("MySQL","host"),
            'port' : int(config.get("MySQL","port")),
            'database' : config.get("MySQL","database"),
            'charset' : 'utf8',
            'collation' : 'utf8_general_ci',
            'buffered' : True
    }

    return sql.connect(**db_params)

def getUserId(conn, tweet, twitter_id, user_type): 
    cursor = conn.cursor()
    try :
        cursor.execute("SELECT id FROM users_user WHERE twitter_id = %s" % twitter_id)
        conn.commit()
        if cursor.rowcount == 1:
            row = cursor.fetchone()
            if row[0] == "None":
                user_id = addUser(conn, tweet, user_type, twitter_id)
            else:
                user_id = row[0]
        else:
            user_id = addUser(conn, tweet, user_type, twitter_id)
    except sql.Error as err :
        print(">>>> Warning: Could not check whether user exists: %s" % str(err))
        print("     Query: %s" % cursor.statement)
        
    cursor.close()
    return user_id


# add a user to the db whether s/he's a sender, was mentioned, or was replied to
def addUser(conn, tweet, user_type, user_id) :
    cursor = conn.cursor()
    # check to see if the user already exists
    try :
        cursor.execute("SELECT id FROM users_user WHERE twitter_id = %s" % user_id)
        conn.commit()
    except sql.Error as err :
        print(">>>> Warning: Could not add User: %s" % str(err))
        print("     Query: %s" % cursor.statement)
    # if the user doesn't already exist
    if cursor.rowcount == 0:
        put_user_query = "INSERT INTO users_user (twitter_id, twitter_name, fullname, followers, following, " \
            "favorites, tweets, timezone) " \
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s )"

        if user_type == "sender":
            values = [
                tweet["user"]["id_str"],
                tweet["user"]["screen_name"],
                tweet["user"]["name"],
                tweet["user"]["followers_count"],
                tweet["user"]["friends_count"],
                tweet["user"]["favourites_count"],
                tweet["user"]["statuses_count"],
                tweet["user"]["time_zone"],
            ]
        elif user_type == "mention":
            values = [
                user_id,
                "", # name
                "", # fullname
                "", # followers
                "", # friends
                "", # favourites
                "", # statuses
                "", # time_zone
            ]
        elif user_type == "reply":
            values = [
                tweet["in_reply_to_user_id"],
                "", # name
                "", # fullname
                "", # followers
                "", # friends
                "", # favourites
                "", # statuses
                "", # time_zone
            ]
        try :
            cursor.execute(put_user_query, values)
            conn.commit()
            user_id = cursor.lastrowid
        except sql.Error as err :
            print(">>>> Warning: Could not add User: %s" % str(err))
            print("     Query: %s" % cursor.statement)
            sys.exit()
        
    cursor.close()
    return user_id

def updateUser(conn, tweet, user_id):
    cursor = conn.cursor()
    
    try :
        cursor.execute("SELECT id FROM users_user WHERE twitter_id = %s AND tweets = 0" % user_id)
        conn.commit()
    except sql.Error as err :
        print(">>>> Warning: Could not add User: %s" % str(err))
        print("     Query: %s" % cursor.statement)
    if cursor.rowcount == 1:
        row = cursor.fetchone()
        user_id = row[0]
        update_user_query = "UPDATE users_user SET " \
            "twitter_name = %s, " \
            "fullname = %s, " \
            "followers = %s, " \
            "following = %s, " \
            "favorites = %s, " \
            "tweets = %s, " \
            "timezone = %s " \
            "WHERE id = %s"
    
        values = [
            tweet["user"]["screen_name"],
            tweet["user"]["name"],
            tweet["user"]["followers_count"],
            tweet["user"]["friends_count"],
            tweet["user"]["favourites_count"],
            tweet["user"]["statuses_count"],
            tweet["user"]["time_zone"],
            user_id,
        ]
        try :
            cursor.execute(update_user_query, values)
            conn.commit()
        except sql.Error as err :
            print(">>>> Warning: Could not update user: %s" % str(err))
            print("     Query: %s" % cursor.statement)        
        finally :
            cursor.close()


# Add a tweet to the DB
def addTweet(conn, tweet) :
    cursor = conn.cursor()

    prefix = "INSERT INTO tweets_tweet (tweet_id, created_at, text, source, iso_language"
    suffix = ") VALUES (%s, %s, %s, %s, %s"
    values = [
        tweet["id_str"],
        datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y').strftime('%Y-%m-%d %H:%M:%S'),
        tweet["text"],
        tweet["source"],
        tweet["lang"]
    ]

    # Optionally include the geo data
    if tweet['geo'] is not None and tweet['geo']['type'] == "Point" :
        prefix = prefix + ", location_geo, location_geo_0, location_geo_1"
        suffix = suffix + ", Point(%s,%s), %s, %s"
        values.extend([
                tweet["geo"]["coordinates"][0],
                tweet["geo"]["coordinates"][1],
                tweet["geo"]["coordinates"][0],
                tweet["geo"]["coordinates"][1]
        ])

    suffix = suffix + ")"
    query = (prefix + suffix)

    try :
        cursor.execute(query, values)
        conn.commit()
        return True
    except sql.Error as err :
        print(">>>> Warning: Could not add Tweet: %s" % str(err))
        print("     Query: %s" % cursor.statement)        
        return False
    finally :
        cursor.close()

# Add hashtag entities to the DB
def addHashtags(conn, tweet) :
    cursor = conn.cursor()

    query = "INSERT INTO hashtags_hashtag (tweet_id_id, text, index_start, index_end) " \
            "VALUES(%s, %s, %s, %s)"

    for hashtag in tweet['entities']['hashtags'] :
        values = [
                tweet["id_str"],
                hashtag["text"],
                hashtag["indices"][0],
                hashtag["indices"][1]
        ]

        try :
            cursor.execute(query, values)
            conn.commit()
        except sql.Error as err :
            print(">>>> Warning: Could not add hashtag: %s" % str(err))
            print("     Query: %s" % cursor.statement)
    cursor.close()

# Add user mention entities to the DB
def addUserMentions(conn, tweet) :
    cursor = conn.cursor()

    mentions_query = "INSERT INTO mentions_mention (tweet_id_id, screen_name, name, index_start, index_end) " \
            "VALUES(%s, %s, %s, %s, %s)"

    user_mentions_query = "INSERT INTO mentions_mention_id_str (mention_id, user_id) " \
        "VALUES(%s, %s)"

    for mention in tweet['entities']['user_mentions'] :
        
        # add the mention to the mentions table
        mention_values = [
                tweet["id_str"],
                mention["screen_name"],
                mention["name"],
                mention["indices"][0],
                mention["indices"][1]
        ]

        try :
            cursor.execute(mentions_query, mention_values)
            conn.commit()
            mention_id = cursor.lastrowid
        except sql.Error as err :
            print(">>>> Warning: Could not add Mention: %s" % str(err))
            print("     Query: %s" % cursor.statement)
            
        user_id = getUserId(conn, tweet, mention["id_str"], "mention")
            
        # add the relationship mention-user to the appropriate table
        user_mention_values = [
            mention_id,
            user_id
        ]
        try :
            cursor.execute(user_mentions_query, user_mention_values)
            conn.commit()
        except sql.Error as err :
            print(">>>> Warning: Could not add mention: %s" % str(err))
            print("     Query: %s" % cursor.statement)
    cursor.close()

# Add all URL entities to the DB
def addLinks(conn, tweet) :
    cursor = conn.cursor()

    query = "INSERT INTO links_link (tweet_id_id, url, expanded_url, display_url, index_start, index_end) " \
            "VALUES(%s, %s, %s, %s, %s, %s)"

    for url in tweet['entities']['urls'] :
        values = [
                tweet["id_str"],
                url["url"],
                url["expanded_url"] if "expanded_url" in url else "",
                url["display_url"] if "display_url" in url else "",
                url["indices"][0],
                url["indices"][1]
        ]

        try :
            cursor.execute(query, values)
            conn.commit()
        except sql.Error as err :
            print(">>>> Warning: Could not add link: %s" % str(err))
            print("     Query: %s" % cursor.statement)
    cursor.close()

# Add User_Tweet relationship to the many-to-many table
def addUserTweets(conn, tweet):
    cursor = conn.cursor()
    
    try :
        user_id = getUserId(conn, tweet, tweet["user"]["id"], "sender")
    except :
        print "Can't getUserId for %s" % tweet["user"]["id"]
        sys.exit()
    
    # insert source user
    source_query = "INSERT INTO users_userstweets (user_id, tweet_id, source, target) " \
        "VALUES(%s, %s, %s, %s)"

    values = [user_id, tweet["id_str"], 1, 0]
    try:
        cursor.execute(source_query, values)
        conn.commit()
    except sql.Error as err :
        print(">>>> Warning: Could not add source user info: %s" % str(err))
        print("     Query: %s" % cursor.statement)

    # insert target user (if there is one)
    if tweet["in_reply_to_user_id"] :
        # check to see if the user exists
        user_id = getUserId(conn, tweet, tweet["in_reply_to_user_id"], "reply")
        
        target_query = "INSERT INTO users_userstweets (user_id, tweet_id, source, target) " \
            "VALUES(%s, %s, %s, %s)"

        values = [tweet["in_reply_to_user_id"], tweet["id_str"], 0, 1]
        try:
            cursor.execute(target_query, values)
            conn.commit()
        except sql.Error as err :
            print(">>>> Warning: Could not add target user info: %s" % str(err))
            print("     Query: %s" % cursor.statement)
    cursor.close()    # Add User_Tweet relationship to the many-to-many table

# Main function
if __name__ == '__main__' :
    config = SafeConfigParser()
    script_dir = os.path.dirname(__file__)
    config_file = os.path.join(script_dir, 'config/settings.cfg')
    config.read(config_file)
    
    # Display startup info
    print("vvvvv Start:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    print("Connecting to database...")

    try :
        run_total_count = 0
        conn = connect()
        print("Connected")

        # Get the Tweets
        dir = config.get('files','outfolder')

        for file in os.listdir(dir):
            f = open(dir+'/'+file, 'r')
            print "Working on %s " % f
            tweets = collections.deque()
            try:
            #   tweets = [json.loads(line) for line in f.readlines()]
                tweets = convert(json.loads(f.read()))
                f.close()
            except ValueError as err:
                print("%s in %s" % (err, file))
                continue
        
            total_results = 0
        
            count = 1
            total = len(tweets)
        
            for tweet in tweets :
        
                # total_results = total_results + 1
                # print "now on tweet %s" % tweet["text"]
        
                # Insert the tweet in the DB
                success = addTweet(conn, tweet)
                # addTweet(conn, tweet)
        
                # Insert the tweet entities in the DB
                if success == False:
                    print("Failed to insert tweets from %s." % file)
                addUserTweets(conn, tweet)
                addHashtags(conn, tweet)
                addUserMentions(conn, tweet)
                addLinks(conn, tweet)
                updateUser(conn, tweet, tweet["user"]["id"])
                # print("Processed %s tweets in %s." % (total_results, file))
                run_total_count = run_total_count + total_results
            print "Done with %s " % f
    except sql.Error as err :
        print(err)
        print("Terminating.")
        sys.exit(1)
    else :
        conn.close()
    finally :
        print("$$$$$ Run total count: " + str(run_total_count))
        print("^^^^^ Stop:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
