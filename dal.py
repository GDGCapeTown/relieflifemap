
# Google App Engine Libs
from google.appengine.ext import db
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions

# Python Libs
import logging
import time
import calendar
import uuid

# Custom Libs
import schemas


def get_events(active=False, limit=None, offset=0, lat=None, lng=None,ids=None):
    q = schemas.Event.all()

    if active != None:
    	q.filter('active =', active)

    return q.fetch(limit=limit, offset=offset)


def get_allowed_users(limit=None):
    return schemas.AllowedUser.all().fetch(limit=limit)
