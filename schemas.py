# Google Libraries
from google.appengine.ext import db
from google.appengine.api.logservice import logservice
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images

# Custom Libraries
import dal

# Python Libs
import datetime
import logging

#
# Event Details
# @author Johann du Toit
#
class Event(db.Model):
	headline = db.StringProperty(required=True)
	area = db.StringProperty()
	reach = db.IntegerProperty()
	active = db.BooleanProperty(default=False)
	description = db.Text()
	how_to_help = db.Text()
	date_of_incident = db.DateTimeProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	lastupdated = db.DateTimeProperty(auto_now_add=True)

#
# Point for the Event Pointer
# @author Johann du Toit
#
class EventPoint(db.Model):
	location = db.GeoPtProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	lastupdated = db.DateTimeProperty(auto_now_add=True)

#
# Allowed users who may login
# @author Johann du Toit
#
class AllowedUser(db.Model):

	name = db.StringProperty(required=True)
	email = db.StringProperty(required=True)

	created = db.DateTimeProperty(auto_now_add=True)
	lastupdated = db.DateTimeProperty(auto_now_add=True)

