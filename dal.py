
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


def get_events(active=False, limit=1, offset=0, lat=None, lng=None):
    q = schemas.Event.all()
    q.filter('active =', active)

    return q.fetch(limit=limit, offset=offset)


def get_allowed_users():
    return schemas.AllowedUser.all().run()
