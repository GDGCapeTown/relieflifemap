# Google Libs
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions

# Python Libs
import hashlib
from datetime import date
import webapp2
import jinja2
import os
import json
import time
import logging

# Custom Libs
import schemas
import dal
import runner

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

# Read Settings file
settings = json.load(open('settings.json'))

#
# Create a Client
# @author Johann
#
class ClientCreateHandler(webapp2.RequestHandler):
	def post(self):
		self.get()

	def get(self):

		# Get the current logged-in user
		user = users.get_current_user()

		# Check Login
		if not user:
			self.redirect(users.create_login_url('/client/create'))

		# Error to show if any
		form_error = False

		# Set Provider
		selected_provider = 'none'

		# Default Provider
		provider_obj = None
		selected_provider = 'none'

		if self.request.get('provider'): 
			
			try:

				selected_provider = int(self.request.get('provider'))

			except:

				self.redirect('/client/create')

		# Check if this is a form post
		if self.request.POST.get('form_client_create'):

			# Assign Local cleaned parameters
			client_name = str(self.request.POST.get('form_client_name')).strip()
			client_description = str(self.request.POST.get('form_client_description')).strip()
			client_provider = str(self.request.POST.get('form_client_provider')).strip()

			if selected_provider is not 'none':
				db_provider_obj = schemas.Provider.get_by_id(int(selected_provider))

				if db_provider_obj is not None and db_provider_obj is not False:
						
					# Ok so let's check if they are a member
					membership_obj = dal.membership_by_user(db_provider_obj, user)
					if membership_obj is not None and membership_obj is not False:

						provider_obj = db_provider_obj

			# Valdidate
			if not self.request.POST.get('form_client_name') or len(client_name) == 0:
				# Name is Required
				form_error = 'Name of your Client is Required'
			elif not self.request.POST.get('form_client_description') or len(client_description) == 0:
				# Description is Required
				form_error = 'Some Description of your API Client is Required'
			else:

				# Create our API Secret Key
				d = date.today()
				value_key = str(str(d.year) + "-" + str(d.month) + "-" + str(d.day)) + client_name + client_description
				client_secret_token = hashlib.sha1(value_key).hexdigest()

				# Create the Provider Object and Populate
				client_obj = schemas.APIClient(
					name=client_name,
					description=client_description,
					user=user,
					token=client_secret_token,
					provider=provider_obj)

				# Save that sucker
				client_obj.put()

				# Redirect to the profile page
				self.redirect('/client/' + str(client_obj.key().id()))

		# Get the Providers of the Client
		providers = dal.providers_by_user(user)

		locales = {
			'form_error': form_error,
			'title': 'Create API Client',
			'description': '',
			'user': user,
			'post_params': self.request.POST,
			'providers': providers,
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}

		if selected_provider is not 'none':
			locales['selected_provider'] = selected_provider

		template = jinja_environment.get_template('client/create.html')
		self.response.out.write(template.render(locales))

#
# Display Edit information for the client
# @author Johann du Toit
#
class ClientDetailsHandler(blobstore_handlers.BlobstoreUploadHandler):
	def get(self, provider_uid):

		client_obj = schemas.APIClient.get_by_id(int(provider_uid))
		user = users.get_current_user()

		if client_obj is not None and client_obj is not False:
			
			# Get the current date and year
			current_date = int(time.strftime("%d"))
			current_month = int(time.strftime("%m"))
			current_year = int(time.strftime("%Y"))

			# get the calls
			search_apis_calls = dal.search_api_calls(client_obj, current_date, current_month, current_year)
			
			# Local Var with Limit
			daily_limit_local = search_apis_calls.count()

			locales = {
				'title': client_obj.name,
				'description': client_obj.description,
				'user': user,
				'client': client_obj,
				'remaining_limit': daily_limit_local,
				'session': dal.return_and_global_session_update(self),
				'is_current_user_admin': users.is_current_user_admin()
			}

			# Ok so Provider exists.
			# Now check if this is a logged in user and if they are a member of this provider.
			# If so we rather so a dashboard and edit properties and controls.
			if user:
				
				# Check if user is allowed to edit and view this client
				if user == client_obj.user:


					# Delete the Client
					if self.request.get('delete'):

						client_obj.status = False
						client_obj.put()
						self.redirect('/profile')

					# Reset Key
					if self.request.get('reset'):

						# Generate a Token
						d = date.today()
						import datetime
						value_key = str(datetime.datetime.now().strftime("%S")) + "-" + str(str(d.year) + "-" + str(d.month) + "-" + str(d.day)) + client_obj.name + client_obj.description
						client_secret_token = hashlib.sha1(value_key).hexdigest()

						# Save
						client_obj.token = client_secret_token
						client_obj.put()

						# Redirect to Client
						self.redirect('/client/' + str(client_obj.key().id()))

					# Create the Template
					template = jinja_environment.get_template('client/details.html')

					# Write out template
					self.response.out.write(template.render(locales))

				else:

					# Redirect to the profile
					self.redirect('/profile')

			else:

				# Redirect to the profile
				self.redirect('/profile')

		else:

			# Redirect the profile
			self.redirect('/profile')

	def post(self):

		# Direct to the Post Handler
		self.get()