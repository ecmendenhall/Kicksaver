from __future__ import division
from google.appengine.ext import db
from models import Project
from urllib import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from time import strptime, mktime
import tweepy
import logging

CONSUMER_KEY = #'Your consumer key goes here!'
CONSUMER_SECRET = #'Same for your consumer secret!'
ACCESS_KEY = #'And your access key...'
ACCESS_SECRET = #'...and access secret. See the Tweepy documentation for details.'

def start_API(c_key, c_secret, a_key, a_secret):
    """ Initialize the Twitter API and authenticate via OAuth. """
    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_key, a_secret)
    return tweepy.API(auth)

def get_last_project(api):
    """ Get the url of the last few projects tweeted. """
    last_tweets = [tweet.text for tweet in api.user_timeline()[0:10]]
    projects = []
    for tweet in last_tweets:
        url = tweet.find('http://')
        if url != -1:
            project = urlopen(tweet[url:])
            projects.append(project.geturl())
    return projects

def get_close_project(budget, last_projects):
    """ Get a new project to tweet, but don't repeat the last. """
    p = Project.all()
    projects = p.filter('left < ', budget).fetch(10)
    project = projects.pop()
    while project.link in last_projects:
        project = projects.pop()
    return project

def get_soon_project(budget, last_projects):
    """ Get a new project to tweet, but don't repeat the last. """
    p = Project.all()
    projects = [project for project in p.filter('left < ', budget)]
    timeleft = lambda i: i.end - datetime.now() + timedelta(0, 14400)
    projects.sort(key=timeleft, reverse=True)
    project = projects.pop()
    while project.link in last_projects:
        project = projects.pop()
    return project

def tweet_project(project, api):
    """ Format and tweet project details. """
    tweet_string = '"%s" is $%d from its goal with %s left: %s'
    p = urlopen(project.link).read()
    project_soup = BeautifulSoup(p)
    escaped_name = project_soup.select('#name')[0].get_text()[1:-1]
    name = HTMLParser.HTMLParser().unescape(escaped_name)
    end_time = project_soup.select('.ksr_page_timer')[0]['data-end_time']
    end_struct = strptime(end_time[:-6], '%a, %d %b %Y %H:%M:%S')
    end_datetime = datetime.fromtimestamp(mktime(end_struct))
    time_left = end_datetime - datetime.now() + timedelta(0, 14400)
    if time_left.days:
        hours = str(int(round(time_left.seconds / 3600)))
        time_string = "%s days, %s hours" % (str(time_left.days), hours)
    else:
        hours = str(int(round(time_left.seconds / 3600)))
        time_string = "%s hours" % hours
    url = project.link
    left = project.left
    tweet_text = tweet_string % (name, left, time_string, url)
    api.update_status(tweet_text)

def main():
    api = start_API(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    last_project = get_last_project(api)
    close_project = get_close_project(500, last_project)
    soon_project = get_soon_project(500, last_project)
    tweet_project(close_project, api)
    tweet_project(soon_project, api)

if __name__ == '__main__':
    main()
