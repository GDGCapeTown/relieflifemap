# Google Apis
from google.appengine.api import users
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions
from google.appengine.ext import db

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

		event_objs = []

		user = users.get_current_user()

		# Get the events
		event_objs = dal.get_events(active=True)

		output_event = []

		for event_obj in event_objs:

			output_event.append( {

				'id': event_obj.key().id(),
				'headline': event_obj.headline,
				'description': event_obj.description,
				'reach': event_obj.reach,
				'how_to_help': event_obj.how_to_help,
				'lat': event_obj.location.lat,
				'lng': event_obj.location.lon

			} )

		self.response.out.write(json.dumps(output_event))

#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class ListEventsHandler(webapp2.RequestHandler):
	def get(self):

		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

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

		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

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

		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

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
class SaveEventsHandler(webapp2.RequestHandler):

	def post(self):

		user = users.get_current_user()
		if not user:
			self.response.out.write('not logged in')

		event_obj = None

		if self.request.POST.get('event_id'):

			event_obj = schemas.Event.get_by_id(int(self.request.POST.get('event_id')))

			if not event_obj:

				# Back to List
				self.response.out.write('no such obj')

		else:

			event_obj = schemas.Event()

		lats = str(self.request.POST.get('lat')).strip().split(',')
		lngs = str(self.request.POST.get('lng')).strip().split(',')

		# Post Update
		event_obj.headline = str(self.request.POST.get('headline')).strip()
		event_obj.reach = int( str(self.request.POST.get('reach')).strip() )
		event_obj.description = str(self.request.POST.get('description')).strip()
		event_obj.how_to_help = str(self.request.POST.get('how_to_help')).strip()
		event_obj.active = True
		event_obj.location = db.GeoPt(lat=lats[0],lon=lngs[0])
		event_obj.put()

		for i in range(0,len(lats)):

			point_obj = schemas.EventPoint()
			point_obj.location = db.GeoPt(lat=lats[i],lon=lngs[i])
			point_obj.put()

		self.response.out.write('ok')


#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class DeleteEventsHandler(webapp2.RequestHandler):
	def get(self, event_uid):

		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		# Delete the Event
		event_obj = schemas.Event.get_by_id(int(event_uid))
		if event_obj:
			event_obj.delete()

		self.redirect('/manage')

