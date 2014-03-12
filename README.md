user-timeline-tools (v.1 - March 12, 2014)
==========================================

user-timeline-tools are a set of Python scripts that get UserTimeline data from Twitter and parse it into a MySQL database so that a Django app can serve it up.

Python Versions
---------------
user-timeline-tools was written for Python 2.7. It has not been testing on other versions.

What You Need Before you Start
------------------------------
You need a list of Twitter screen names stored in a plain text file, one name per line.

Setup
-----
1. Create a MySQL database using ```schema.mysql```
2. Set your variables to the right values in 	```getUserTimeline.py```
3. Run ```getUserTimeline.py```
4. Create a ```settings.cfg``` that looks like ```settings_example.cfg``` but with your values
5. Run ```parseUserTimeline.py``` (will take a while, maybe even a day)
