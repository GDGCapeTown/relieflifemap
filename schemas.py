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
# Provider Schema
# @author Johann du Toit
#
class Event(db.Model):
	headline = db.StringProperty(required=True)
	area = db.IntegerProperty()
	area_name = db.StringProperty(required=True)

	severity = db.IntegerProperty()
	location = db.GeoPtProperty(required=True)

	active = db.BooleanProperty(default=False)

	description = db.Text()
	how_to_help = db.Text()
	date_of_incident = db.DateTimeProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	lastupdated = db.DateTimeProperty(auto_now_add=True)

#
# 
# @author Johann du Toit
#
class AllowedUser(db.Model):

	name = db.StringProperty(required=True)
	email = db.StringProperty(required=True)

	created = db.DateTimeProperty(auto_now_add=True)
	lastupdated = db.DateTimeProperty(auto_now_add=True)

