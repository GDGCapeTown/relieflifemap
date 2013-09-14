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
class ListEventsHandler(webapp2.RequestHandler):
	def get(self):

		# Get the events
		event_objs = [] # dal.get_events()

		# Locales
		locales = {
			'title': 'Welcome',
			'description': 'Search Microchips',
			'event_objs': event_objs,
			'user': users.get_current_user()
		}

		# Render the template
		template = jinja_environment.get_template('admin/events/list.html')
		self.response.out.write(template.render(locales))



#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class CreateEventsHandler(webapp2.RequestHandler):
	def get(self):

		# Locales
		locales = {
			'title': 'Welcome',
			'description': 'Search Microchips',
			'event_objs': event_objs,
			'user': users.get_current_user(),
			'errors': []
		}

		# Render the template
		template = jinja_environment.get_template('admin/events/save.html')
		self.response.out.write(template.render(locales))


#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class UpdateEventsHandler(webapp2.RequestHandler):
	def get(self):

		# Get the events
		event_objs = [] # dal.get_events()

		# Locales
		locales = {
			'title': 'Welcome',
			'description': 'Search Microchips',
			'event_objs': event_objs,
			'user': users.get_current_user()
		}

		# Render the template
		template = jinja_environment.get_template('admin/events/list.html')
		self.response.out.write(template.render(locales))


#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class DeleteEventsHandler(webapp2.RequestHandler):
	def get(self, event_uid):

		event_obj = schemas.Event.get_by_id(int(event_uid))
		event_obj.remove()
		self.redirect('/manage')
		
