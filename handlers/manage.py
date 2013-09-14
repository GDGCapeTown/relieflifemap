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
import schemas

# Setup our Jinja Runner
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class ListEventsHandler(webapp2.RequestHandler):
	def get(self):

		# Get the events
		event_objs = dal.get_events()

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
			'event': {},
			'user': users.get_current_user(),
			'errors': []
		}

		# Render the template
		template = jinja_environment.get_template('admin/events/save.html')
		self.response.out.write(template.render(locales))

	def post(self):

		event_obj = schemas.Event(

				headline="test #1",
				area_name="test 2",
				location=None

			)

		event_obj.put()

		self.redirect('/manage')


#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class UpdateEventsHandler(webapp2.RequestHandler):
	def get(self, event_uid):

		event_obj = schemas.Event.get_by_id(int(event_uid))

		if event_obj:

			# Locales
			locales = {
				'title': 'Welcome',
				'description': 'Search Microchips',
				'event': event_obj,
				'user': users.get_current_user()
			}

			# Render the template
			template = jinja_environment.get_template('admin/events/save.html')
			self.response.out.write(template.render(locales))

		else:
			self.redirect('/manage')

	def post(self):

		event_obj = schemas.Event.get_by_id(int(event_uid))

		if event_obj:

			# Post Update
			event_obj.headline = "Test #1"
			event_obj.put()

		else:

			# Back to List
			self.redirect('/manage')


#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class DeleteEventsHandler(webapp2.RequestHandler):
	def get(self, event_uid):

		# Delete the Event
		event_obj = schemas.Event.get_by_id(int(event_uid))
		if event_obj:
			event_obj.delete()

		self.redirect('/manage')

