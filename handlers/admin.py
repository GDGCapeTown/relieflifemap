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
import mailer

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

# Read Settings file
settings = json.load(open('settings.json'))

#
# Admins the Provider Lists
# @author Johann
#
class AdminOverviewHandler(webapp2.RequestHandler):
	def post(self):
		self.get()

	def get(self):

		# Redirect to Providers
		self.redirect('/admin/providers')

#
# Admins the Provider Lists
# @author Johann
#
class AdminProviderListHandler(webapp2.RequestHandler):
	def post(self):
		self.get()

	def get(self):

		# Get the current logged-in user
		user = users.get_current_user()

		# Get the Session
		session = dal.return_and_global_session_update(self)

		# Check Login
		if not user:
			self.redirect(users.create_login_url('/admin/providers'))

		# Check if they are a admin
		if users.is_current_user_admin() == False:
			self.redirect('/')

		# Check Provider
		if self.request.get('provider') and self.request.get('action'):

			# Get ID's
			provider_id = int(self.request.get('provider'))
			action_str = self.request.get('action')

			# Provider Object
			provider_obj = schemas.Provider.get_by_id(int(self.request.get('provider')))
			
			# Check if it's a Valid Provider
			if provider_obj is not None and provider_obj is not False:

				# What action
				if action_str == "remove" or action_str == "delete":

					# Get the members to send the Mail to
					members = dal.memberships_by_provider(provider_obj)

					# Loop and Mail the Members
					for member in members:

						# Send Mail to Member
						template_locales = {
							'title': str(provider_obj.name) + ' has been removed from IdentiChip.org',
							'description': str(provider_obj.name) + ' has been removed from IdentiChip.org',
							'subject': str(provider_obj.name) + ' has been removed from IdentiChip.org',
							'provider': provider_obj
						}

						# The Form parameters were validated
						mailer.send(
							to=str(member.user.email()),
							reply_to='noreply@identichip.org',
							subject=template_locales['subject'],
							view='mail/provider/provider_deleted.html',
							locales=template_locales)

					# Remove Members
					db.delete(dal.memberships_by_provider(provider_obj))

					# Delete the Provider
					db.delete(provider_obj)

				elif action_str == "approve":

					# Set Settings
					provider_obj.approved = self.request.get('flag') == "on"
					
					# Get the members to send the Mail to
					members = dal.memberships_by_provider(provider_obj)

					# Loop and Mail the Members
					for member in members:

						# Is on
						if self.request.get('flag') == "on":

							# Text
							text_str = str(provider_obj.name) + ' has been Approved'

							# Send Mail to Member
							template_locales = {
								'title': text_str,
								'description': text_str,
								'subject': text_str,
								'provider': provider_obj
							}

							# The Form parameters were validated
							mailer.send(
								to=str(member.user.email()),
								reply_to='noreply@identichip.org',
								subject=template_locales['subject'],
								view='mail/provider/provider_approved.html',
								locales=template_locales)

						else:

							# Text
							text_str = str(provider_obj.name) + ' has had it\'s approval status removed'

							# Send Mail to Member
							template_locales = {
								'title': text_str,
								'description': text_str,
								'subject': text_str,
								'provider': provider_obj
							}

							# The Form parameters were validated
							mailer.send(
								to=str(member.user.email()),
								reply_to='noreply@identichip.org',
								subject=template_locales['subject'],
								view='mail/provider/provider_not_approved.html',
								locales=template_locales)

					# Save
					provider_obj.put()

				elif action_str == "tested":

					# Set Settings
					provider_obj.tested = self.request.get('flag') == "on"

					# Get the members to send the Mail to
					members = dal.memberships_by_provider(provider_obj)

					# Loop and Mail the Members
					for member in members:

						# Is on
						if self.request.get('flag') == "on":

							# Text
							text_str = str(provider_obj.name) + ' has been Marked as Tested by a Administrator'

							# Send Mail to Member
							template_locales = {
								'title': text_str,
								'description': text_str,
								'subject': text_str,
								'provider': provider_obj
							}

							# The Form parameters were validated
							mailer.send(
								to=str(member.user.email()),
								reply_to='noreply@identichip.org',
								subject=template_locales['subject'],
								view='mail/provider/provider_tested.html',
								locales=template_locales)

						else:

							# Text
							text_str = str(provider_obj.name) + ' has been had it\'s tested status removed by a Administrator'

							# Send Mail to Member
							template_locales = {
								'title': text_str,
								'description': text_str,
								'subject': text_str,
								'provider': provider_obj
							}

							# The Form parameters were validated
							mailer.send(
								to=str(member.user.email()),
								reply_to='noreply@identichip.org',
								subject=template_locales['subject'],
								view='mail/provider/provider_not_tested.html',
								locales=template_locales)

					# Save
					provider_obj.put()

				# Tell the Provider they have been included in the searches
				if provider_obj.approved and provider_obj.tested:

					# Get the members to send the Mail to
					members = dal.memberships_by_provider(provider_obj)

					# Loop and Mail the Members
					for member in members:

						# Text
						text_str = str(provider_obj.name) + ' is now regonized as a trusted provider on Identichip.org'

						# Send Mail to Member
						template_locales = {
							'title': text_str,
							'description': text_str,
							'subject': text_str,
							'provider': provider_obj
						}

						# The Form parameters were validated
						mailer.send(
							to=str(member.user.email()),
							reply_to='noreply@identichip.org',
							subject=template_locales['subject'],
							view='mail/provider/provider_included.html',
							locales=template_locales)

				# Redirect
				self.redirect('/admin/providers#provider_block_' + str(provider_obj.key().id()))

			# Else redirect
			else:
				self.redirect('/admin/providers')

		# Get Providers
		providers_list = dal.get_list_of_providers()

		# Counters
		approved_providers_count = 0
		accepted_providers_count = 0
		tested_providers_count = 0

		# Count
		for provider_list_obj in providers_list:

			# Count Approved
			if provider_list_obj.approved and provider_list_obj.tested:

				# Count
				accepted_providers_count += 1

			# Count Approved
			elif not provider_list_obj.approved:

				# Count
				approved_providers_count += 1

			# Counter
			elif not provider_list_obj.tested:

				# Count
				tested_providers_count += 1

		# Locales
		locales = {
			'title': 'Manage Approved Providers',
			'description': 'Providers',
			'user': users.get_current_user(),
			'session': session,
			'providers': providers_list,
			'approved_providers_count': approved_providers_count,
			'accepted_providers_count': accepted_providers_count,
			'tested_providers_count': tested_providers_count,
			'is_current_user_admin': users.is_current_user_admin()
		}

		# Render the template
		template = jinja_environment.get_template('admin/providers.html')
		self.response.out.write(template.render(locales))