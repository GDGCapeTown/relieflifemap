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
class Provider(db.Model):
	name = db.StringProperty(required=True)
	logo = blobstore.BlobReferenceProperty()
	secret = db.StringProperty()
	website = db.StringProperty()
	api_url = db.StringProperty()
	approved = db.BooleanProperty()
	tested = db.BooleanProperty()
	groups = db.StringProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	lastupdated = db.DateTimeProperty(auto_now_add=True)

	# Returns the Logo URL
	def logo_url(self, size):
		if self.logo:
			return images.get_serving_url(self.logo.key(), size)
		else:
			return "/img/defaults/provider.png"
