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
import json
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
class ListAPIEventsHandler(webapp2.RequestHandler):
	def get(self):

		# Get the events
		event_objs = dal.get_events(active=False)

		output_event = []

		for event_obj in event_objs:

			output_event.append( {

				'headline': event_obj.headline,
				'area_name': event_obj.area_name,
				'description': event_obj.description,
				'how_to_help': event_obj.how_to_help,

			} )

		self.response.out.write(json.dumps(output_event))

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


class ViewEventsHandler(webapp2.RequestHandler):
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
		template = jinja_environment.get_template('admin/events/view.html')
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

		headline = str(self.request.POST.get('headline')).strip()
		area_name = str(self.request.POST.get('area_name')).strip()

		event_obj = schemas.Event(

				headline=headline,
				area_name=area_name,
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
			event_obj.headline = str(self.request.POST.get('headline')).strip()
			event_obj.area_name = str(self.request.POST.get('area_name')).strip()
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

