# Google Apis
from google.appengine.api import users
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions

# Python Apis
import webapp2
import os
import jinja2
import os
import time
import logging
import uuid

# Custom Apis
import dal

# Setup our Jinja Runner
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class LoginHandler(webapp2.RequestHandler):
	def get(self):

		# Normal Google User Account
		self.redirect(users.create_login_url('/auth'))

#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class PostLoginHandler(webapp2.RequestHandler):
	def get(self):

		# Normal Google User Account
		user = users.get_current_user()

		# Redirect to manage
		self.redirect('/manage')


