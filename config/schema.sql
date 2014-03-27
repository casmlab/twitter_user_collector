# ************************************************************
# Sequel Pro SQL dump
# Version 4096
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: localhost (MySQL 5.5.30-1)
# Database: user-timeline-test
# Generation Time: 2014-03-26 18:14:39 +0000
# ************************************************************


# Dump of table hashtags_hashtag
# ------------------------------------------------------------

CREATE TABLE `hashtags_hashtag` (
  `hashtag_id` int(11) NOT NULL AUTO_INCREMENT,
  `tweet_id_id` varchar(21) NOT NULL,
  `text` varchar(145) NOT NULL,
  `index_start` int(11) NOT NULL,
  `index_end` int(11) NOT NULL,
  PRIMARY KEY (`hashtag_id`),
  KEY `hashtags_hashtag_bd1043ec` (`tweet_id_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table links_link
# ------------------------------------------------------------

CREATE TABLE `links_link` (
  `url_id` int(11) NOT NULL AUTO_INCREMENT,
  `tweet_id_id` varchar(21) NOT NULL,
  `url` varchar(255) NOT NULL,
  `expanded_url` varchar(400) NOT NULL,
  `display_url` varchar(255) NOT NULL,
  `index_start` int(11) NOT NULL,
  `index_end` int(11) NOT NULL,
  PRIMARY KEY (`url_id`),
  KEY `links_link_bd1043ec` (`tweet_id_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table mentions_mention
# ------------------------------------------------------------

CREATE TABLE `mentions_mention` (
  `mention_id` int(11) NOT NULL AUTO_INCREMENT,
  `tweet_id_id` varchar(21) NOT NULL,
  `screen_name` varchar(45) NOT NULL,
  `name` varchar(45) NOT NULL,
  `index_start` int(11) NOT NULL,
  `index_end` int(11) NOT NULL,
  PRIMARY KEY (`mention_id`),
  KEY `mentions_mention_bd1043ec` (`tweet_id_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table mentions_mention_id_str
# ------------------------------------------------------------

CREATE TABLE `mentions_mention_id_str` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mention_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `mention_id` (`mention_id`,`user_id`),
  KEY `mentions_mention_id_str_04583a85` (`mention_id`),
  KEY `mentions_mention_id_str_6340c63c` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table tweets_tweet
# ------------------------------------------------------------

CREATE TABLE `tweets_tweet` (
  `tweet_id` varchar(21) NOT NULL,
  `created_at` datetime NOT NULL,
  `text` varchar(255) NOT NULL,
  `source` varchar(255) NOT NULL,
  `location_geo` longtext DEFAULT NULL,
  `location_geo_0` decimal(14,10) DEFAULT NULL,
  `location_geo_1` decimal(14,10) DEFAULT NULL,
  `iso_language` varchar(3) NOT NULL,
  PRIMARY KEY (`tweet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

# Dump of table users_user
# ------------------------------------------------------------

CREATE TABLE `users_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `twitter_id` varchar(21) NOT NULL,
  `twitter_name` varchar(55) NOT NULL,
  `fullname` varchar(45) NOT NULL,
  `followers` int(11) NOT NULL,
  `following` int(11) NOT NULL,
  `favorites` int(11) NOT NULL,
  `tweets` int(11) NOT NULL,
  `timezone` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `twitter_id` (`twitter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table users_userstweets
# ------------------------------------------------------------

CREATE TABLE `users_userstweets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(21) NOT NULL,
  `tweet_id` varchar(21) NOT NULL,
  `source` tinyint(1) NOT NULL,
  `target` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `users_userstweets_6340c63c` (`user_id`),
  KEY `users_userstweets_36542d72` (`tweet_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
