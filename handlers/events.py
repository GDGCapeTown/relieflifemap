# Google Apis
from google.appengine.api import users
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions
from google.appengine.ext import db
from google.appengine.api import search
from decimal import Decimal
import math

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

		lat = self.request.get('lat')
		lng = self.request.get('lng')

		user = users.get_current_user()
		output_event = []
		already_in = []

		index = search.Index(name="event_points")
		query_string = "distance(point, geopoint(" + lat + ", " + lng + ")) < 10000" 
		try:
			results = index.search('') 

			# Iterate over the documents in the results
			for scored_document in results:

				id_val = scored_document['event'][0].value

				if id_val not in already_in:

					already_in.append(id_val)
					event_obj = schemas.Event.get_by_id(  long(str(id_val)) )

					if event_obj != None and event_obj.active == True:

						output_event.append( {

							'id': event_obj.key().id(),
							'headline': event_obj.headline,
							'category': event_obj.category,
							'description': event_obj.description,
							'reach': event_obj.reach,
							'how_to_help': event_obj.how_to_help,
							'lat': event_obj.location.lat,
							'lng': event_obj.location.lon,
							'points': event_obj.points.split('@')

						} )

		except search.Error:
			print logging.exception('search failed')
			

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
		index = search.Index(name="event_points")

		if self.request.POST.get('event_id'):

			event_obj = schemas.Event.get_by_id(long(self.request.POST.get('event_id')))

			if not event_obj:

				# Back to List
				self.response.out.write('no such obj')
				return

			else:

				# Delete all past index
				pass

		else:

			# New Event
			event_obj = schemas.Event()

		lats = str(self.request.POST.get('lat')).strip().split(',')
		lngs = str(self.request.POST.get('lng')).strip().split(',')

		point_objs = []
		for i in range(0,len(lats)):
			point_objs.append(str(lats[i]) + "," + str(lngs[i]))

		# Post Update
		event_obj.headline = str(self.request.POST.get('headline')).strip()
		event_obj.reach = int( str(self.request.POST.get('reach')).strip() )
		event_obj.description = str(self.request.POST.get('description')).strip()
		event_obj.how_to_help = str(self.request.POST.get('how_to_help')).strip()
		event_obj.date_of_incident = str(self.request.POST.get('date')).strip()
		event_obj.category = str(self.request.POST.get('category')).strip()
		event_obj.active = True
		event_obj.points = '' + '@'.join(point_objs)
		event_obj.location = db.GeoPt(lat=float(lats[0]),lon=float(lngs[0]))
		event_obj.put()

		indexes_to_save = []

		for i in range(0,len(lats)):

			plat = lats[i]
			plng = lngs[i]

			event_index_obj = search.Document(

				fields=[

					search.TextField(name='event', value=str(event_obj.key().id())),
					search.GeoField(name='point', value=search.GeoPoint( float( plat ) , float(plng)  ))
				
				]
			)

			# ADd to batch that we will add
			index.put(event_index_obj)
			# indexes_to_save.append(event_index_obj)
		
		# Now we batch save all our indexes
		# index.put(indexes_to_save)

		# Dummy OK just so we send something back !
		self.response.out.write('ok')


#
# Acts as the Frontpage when users are not signed in and the dashboard when they are.
# @author Johann du Toit
#
class DisableEventsHandler(webapp2.RequestHandler):
	def get(self, event_uid):

		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		# Delete the Event
		event_obj = schemas.Event.get_by_id(int(event_uid))
		event_obj.active = False
		event_obj.put()

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

