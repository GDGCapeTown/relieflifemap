# Google Libs
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions
from google.appengine.api import memcache

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

# Jinja Environment
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

# Read Settings file
settings = json.load(open('settings.json'))

#
# Lists all providers on the site. Great for some advertisement for the providers :D
# @author Johann du Toit
#
class ProviderListHandler(webapp2.RequestHandler):
	def get(self):

		# Get the current logged-in user
		user = users.get_current_user()

		# Get all the Approved Providers
		providers = dal.approved_providers()

		locales = {
			'title': 'Registered Providers',
			'description': 'Browse all our Registered Providers. These providers have been approved by us and they had to pass numerous requirements to be considered valid.',
			'user': user,
			'providers': providers,
			'provider_count': providers.count(),
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		
		template = jinja_environment.get_template('provider/list.html')
		self.response.out.write(template.render(locales))

#
# Overview of what's required to list a provider
# @author Johann du Toit
#
class ProviderRegisterOverviewHandler(webapp2.RequestHandler):
	def get(self):

		# Get the current logged-in user
		user = users.get_current_user()

		locales = {
			'title': 'Registering a Provider',
			'description': 'Browse all our Registered Providers. These providers have been approved by us and they had to pass numerous requirements to be considered valid.',
			'user': user,
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('provider/checks.html')
		self.response.out.write(template.render(locales))

#
# The Actual Handler to register Providers. This does validation and inserts the records with the detaults.
# @author Johann du Toit
#
class ProviderRegisterHandler(blobstore_handlers.BlobstoreUploadHandler):
	def get(self):

		user = users.get_current_user()

		if user:

			if 'USER_ORGANIZATION' in os.environ:
				user.organization = os.environ['USER_ORGANIZATION']

			session_store = sessions.get_store(request=self.request)
			session = session_store.get_session()

			# Error to show if any
			register_form_error = False

			# Check if this is a form post
			if self.request.POST.get('form_register'):

				# Assign Local cleaned parameters
				provider_name = str(self.request.POST.get('form_provider_name')).strip()
				provider_description = str(self.request.POST.get('form_provider_description')).strip()
				provider_website = str(self.request.POST.get('form_provider_website')).strip()

				# Valdidate
				if not self.request.POST.get('form_provider_name') or len(provider_name) == 0:
					# Name is Required
					register_form_error = 'Name of your Provider is Required'
				elif not self.request.POST.get('form_provider_website') or len(provider_website) == 0 or (not 'http://' in provider_website or 'https://' in provider_website):
					# Website is Required. # We check for http:// or https://
					register_form_error = 'Website of your Provider is Required. The Path must include http:// or https://'
				else:

					# Handle Logo Uploads
					logo = None
					try:
						logo = self.get_uploads()[0]
					except:
						register_form_error = 'Error while uploading Logo'

					# Create our API Secret Key
					d = date.today()
					value_key = str(str(d.year) + "-" + str(d.month) + "-" + str(d.day)) + provider_name + provider_description + provider_website
					provider_secret = hashlib.sha1(value_key).hexdigest()

					# Create the Provider Object and Populate
					provider_obj = schemas.Provider(
						name=provider_name,
						description=provider_description,
						website=provider_website,
						approved=False,
						tested=False,
						logo=logo,
						secret=provider_secret)

					# Save that sucker
					provider_obj.put()

					if self.request.POST.get('form_provider_name') == 'yes' and user.organization and len(user.organization) > 0:

						if 'members' in session:
							for member in session['members']:
								if 'admin' in member and member['admin'] == 'true':
									# Add the current user as the first member
									new_member = users.User(member['email'])
									membership_obj = schemas.ProviderMember(provider=provider_obj,user=new_member)
									membership_obj.put()

					else:
						# Add the current user as the first member
						membership_obj = schemas.ProviderMember(provider=provider_obj,user=user)
						membership_obj.put()

					# The Form parameters were validated
					mailer.send_admin(
						subject='New Provider registered ' + str(provider_obj.name),
						body='New Provider registered ' + str(provider_obj.name))

					# Text
					text_str = 'New Provider Registration Received for IdentiChip'

					# Send Mail to Member
					template_locales = {
						'title': text_str,
						'description': text_str,
						'subject': text_str,
						'provider': provider_obj,
						'user': user
					}

					# Send to Current User
					mailer.send(
						to=str(user.email()),
						reply_to='noreply@identichip.org',
						subject=template_locales['subject'],
						view='mail/provider/provider_new.html',
						locales=template_locales)

					# Redirect to the new Registered Provider
					self.redirect('/provider/' + str(provider_obj.key().id()))

			# Count of the Admins in the Group
			admin_member_count = 0

			if 'members' in session:
				for member in json.loads(str(session['members'])):
					if 'admin' in member and member['admin'] == 'true':
						admin_member_count = admin_member_count + 1

			# Create the registration layout
			locales = {
				'register_form_error': register_form_error,
				'title': 'Register a New Provider',
				'description': 'Search Microchips',
				'user': user,
				'admin_member_count': admin_member_count,
				'session': session,
				'post_params': self.request.POST,
				'upload_url': blobstore.create_upload_url('/provider/register'),
				'session': dal.return_and_global_session_update(self),
				'is_current_user_admin': users.is_current_user_admin()
			}
			template = jinja_environment.get_template('provider/create.html')
			self.response.out.write(template.render(locales))

		else:
			self.redirect(users.create_login_url('/provider/register'))

	def post(self):

		# Keep all code in one place
		self.get()

class ProviderTestHandler(webapp2.RequestHandler):
	def get(self):

		# Just redirect back to profile
		self.redirect('/profile')

	def post(self):

		provider_obj = schemas.Provider.get_by_id(int(self.request.get('provider')))
		user = users.get_current_user()

		if provider_obj is not None and provider_obj is not False:
			
			locales = {
				'title': provider_obj.name,
				'description': provider_obj.description,
				'user': user,
				'provider': provider_obj,
				'session': dal.return_and_global_session_update(self),
				'is_current_user_admin': users.is_current_user_admin()
			}

			# Ok so Provider exists.
			# Now check if this is a logged in user and if they are a member of this provider.
			# If so we rather so a dashboard and edit properties and controls.
			if user:
				
				# Ok so let's check if they are a member
				membership_obj = dal.membership_by_user(provider_obj, user)
				if membership_obj is not None and membership_obj is not False:

					# Get the UID
					uid = self.request.get('uid')

					# Check the UID
					if uid:

						test_url = self.request.get('test_url')

						if test_url or provider_obj.api_url:

							if test_url:
								# Set it for now
								provider_obj.api_url = test_url

							# Ok so run the test
							search_response = runner.search(self.request, uid, [ provider_obj ])

							# Take the only response
							response_obj = search_response.responses[0]

							# Our Local Copy of errors
							parse_errors = []

							if response_obj.parse_errors is not None:
								parse_errors = response_obj.parse_errors

							# Now output result
							self.response.out.write(repr({
								'status': response_obj.status,
								'response': response_obj.raw_response,
								'url': test_url,
								'data': response_obj.data_sent_to_server,
								'parse_errors': parse_errors
							}))

							# If the result was success we set the details api url of this provider to that url
							if provider_obj.approved and response_obj.status == runner.ProviderResponse.STATUS_FOUND and test_url:
								
								# Save and update to tested
								provider_obj.tested = True
								provider_obj.put()

						else:
							self.response.out.write({ 'errors': [ 'Test Url to test again must be provided' ] })

					else:
						self.response.out.write({ 'errors': [ 'UID to search for must be presented' ] })

				else:
					self.response.out.write({ 'errors': ['Current user must be a member of the provider to access the test tool'] })
			else:
				self.response.out.write({ 'errors': ['Authenticated Session required'] })

		else:
			self.response.out.write({ 'errors': ['Not a Valid Provider'] })

class ProviderDetailsHandler(blobstore_handlers.BlobstoreUploadHandler):
	"""
	Handles the Authentication of the Users to the service
	We use the App Engine User Service for this.

	So it's just a redirect actually
	"""
	def get(self, provider_uid):

		provider_obj = schemas.Provider.get_by_id(int(provider_uid))
		user = users.get_current_user()

		if provider_obj is not None and provider_obj is not False:
			
			locales = {
				'title': provider_obj.name,
				'description': 'Dashboard for Provider',
				'user': user,
				'provider': provider_obj,
				'session': dal.return_and_global_session_update(self),
				'is_current_user_admin': users.is_current_user_admin()
			}

			# Ok so Provider exists.
			# Now check if this is a logged in user and if they are a member of this provider.
			# If so we rather so a dashboard and edit properties and controls.
			if user:
				
				# Ok so let's check if they are a member
				membership_obj = dal.membership_by_user(provider_obj, user)
				if membership_obj is not None and membership_obj is not False:

					# Assign post variables
					locales['post_params'] = self.request.POST

					# Provider Information
					form_test_error = False
					form_test_success = False

					# Testing Tool Response
					form_test_response = False

					# Provider response
					form_test_provide_response = False

					# Check if they want to do a form post
					if self.request.POST.get('form_test_tool'):

						# Check the API Url
						if not self.request.POST.get('form_test_api_url'):
							form_test_error = 'Url of the API Endpoint is Required.'
						elif 'http://' not in self.request.POST.get('form_test_api_url') and 'https://' not in self.request.POST.get('form_test_api_url'):
							# Url where we send the information
							form_test_error = 'Url of the API Endpoint is Required. This must include either http:// or https:// and of course we recommend https to keep it secure.'
						elif not self.request.POST.get('form_test_search_uid') or len(str(self.request.POST.get('form_test_search_uid')).lower().strip()) == 0:
							# Search UID is Required
							form_test_error = 'Please provide a valid Search UID to check the endpoint for'
						else:

							# Assign the test url
							provider_obj.api_url = str(self.request.POST.get('form_test_api_url')).strip()

							# Post Params
							search_uid = str(self.request.POST.get('form_test_search_uid')).lower().strip()

							# Ok so run the test
							search_response = runner.search(self.request, str(search_uid), [ provider_obj ])

							# Show the output
							form_test_response = search_response

							# Assign the provider response
							form_test_provide_response = search_response.responses[0]

							# Check if the result is true, if so we update them as tested
							if form_test_provide_response.status == runner.ProviderResponse.STATUS_FOUND:

								# Assign the Boolean
								provider_obj.tested = True
								provider_obj.put()

								# Success !
								form_test_success = 'We tested the new Url and we got a valid response from the server. After which we set the new url as the default one.'

							else:
								form_test_error = 'Response from Server was not a successfull response. Please check the response that was returned and verify that everthing is working and setup. We will not update the API url until this test is passed.'

					# Param Assignment
					locales['form_test_error'] = form_test_error
					locales['form_test_success'] = form_test_success
					locales['form_test_response'] = form_test_response
					locales['form_test_provide_response'] = form_test_provide_response

					if provider_obj.approved and provider_obj.tested:

						register_form_error = False
						register_form_success = False

						# Check if this is a form post
						if self.request.POST.get('form_provider_update'):

							# Assign Local cleaned parameters
							provider_name = str(self.request.POST.get('form_provider_name')).strip()
							provider_description = str(self.request.POST.get('form_provider_description')).strip()
							provider_website = str(self.request.POST.get('form_provider_website')).strip()

							# Valdidate
							if not self.request.POST.get('form_provider_name') or len(provider_name) == 0:
								# Name is Required
								register_form_error = 'Name of your Provider is Required'
							elif not self.request.POST.get('form_provider_website') or len(provider_website) == 0 or (not 'http://' in provider_website or 'https://' in provider_website):
								# Website is Required. # We check for http:// or https://
								register_form_error = 'Website of your Provider is Required. The Path must include http:// or https://'
							else:

								provider_obj.name = provider_name
								provider_obj.description = provider_description
								provider_obj.website = provider_website

								# Handle Logo Uploads
								if len(self.get_uploads()) > 0:
									try:
										logo = self.get_uploads()[0]
										# provider_obj.logo.delete()
										provider_obj.logo = logo
									except Exception as e:
										print e
										register_form_error = 'Error while uploading Logo'

								# Save that sucker
								provider_obj.put()

								self.redirect('/provider/' + str(provider_obj.key().id()) + "?section=profile")

								register_form_success = 'Provider was updated succesfully.'

						locales["register_form_error"] = register_form_error
						locales['register_form_success'] = register_form_success
						locales['upload_url'] = blobstore.create_upload_url('/provider/' + str(provider_obj.key().id()) + "?section=profile")

						# Statistics

						year = int(time.strftime("%Y"))

						if self.request.get('year'):
							try:
								year = int(self.request.get('year'))
							except:
								pass

						search_count = memcache.get("search_count_" + str(year))
						if search_count is None:
							search_count = db.GqlQuery("SELECT * FROM UserSearchDetail WHERE created > DATE(:1, 1, 1) AND created < DATE(:2, 12, 31) AND provider = :3", year, year, provider_obj).count()

							if not memcache.add("search_count_" + str(year), search_count, 60*10):
								pass

						success_search_count = memcache.get("success_search_count_" + str(year))
						if success_search_count is None:
							success_search_count = db.GqlQuery("SELECT * FROM UserSearchDetail WHERE success_status = True AND created > DATE(:1, 1, 1) AND created < DATE(:2, 12, 31) AND provider = :3", year, year, provider_obj).count()

							if not memcache.add("success_search_count_" + str(year), success_search_count, 60*10):
								pass

						search_contact_count = memcache.get("search_contact_count_" + str(year))
						if search_contact_count is None:
							search_contact_count = db.GqlQuery("SELECT * FROM UserSearchDetail WHERE email_sent = True AND created > DATE(:1, 1, 1) AND created < DATE(:2, 12, 31) AND provider = :3", year, year, provider_obj).count()

							if not memcache.add("search_contact_count_" + str(year), search_contact_count, 60*10):
								pass

						stats = memcache.get("stat_page_" + str(year))
						if stats is None:
							stats = []

							responses = dal.get_stats({
								'year': int(year),
								'provider': provider_obj
							})
						
							stat = {
								'year': int(year),
								'countries': dal.parse_out_countries(responses),
								'cities': dal.parse_out_cities(responses)
							}
							stats.insert(0, stat)

							if not memcache.add("stat_page_" + str(year), stats, 60*10):
								pass

						locales['stats' ] = stats
						locales['current_year' ] = year
						locales['search_count'] = search_count
						locales['search_contact_count'] = search_contact_count
						locales['success_search_count'] = success_search_count

						# Show the Dashboard
						section = 'dashboard'
						if self.request.get('section'):
							section = str(self.request.get('section')).strip().lower()

						user.organization = os.environ['USER_ORGANIZATION']

						session_store = sessions.get_store(request=self.request)
						session = session_store.get_session()

						locales['user'] = user
						locales['members'] = dal.memberships_by_provider(provider_obj)

						if 'members' in session:

							list_of_member_emails = []
							for cmember in locales['members']:
								list_of_member_emails.append(cmember.user.email())

							domain_members = []

							for dmember in json.loads(str(session['members'])):
								if dmember['email'] not in list_of_member_emails:
									domain_members.append(dmember)

							locales['domain_members'] = domain_members
						else:
							locales['domain_members'] = False

						locales['request'] = self.request
						locales['section'] = section
						locales['user_org'] = os.environ['USER_ORGANIZATION']
						locales['years'] = xrange(provider_obj.created.year, int(time.strftime("%Y"))+1)
						locales['current_year'] = year
						locales['membership'] = membership_obj

						clients = dal.get_clients_by_provider(provider_obj)
						locales['clients'] = clients
						locales['client_count'] = clients.count()

						template = jinja_environment.get_template('provider/dashboard.html')
						self.response.out.write(template.render(locales))

					elif not provider_obj.approved:

						# Show the Approval Waiting Page
						template = jinja_environment.get_template('provider/being_approved.html')
						self.response.out.write(template.render(locales))

					elif not provider_obj.tested:

						# Show the Approval Waiting Page
						template = jinja_environment.get_template('provider/not_tested.html')
						self.response.out.write(template.render(locales))

					else:
						self.redirect('/')

				else:
					template = jinja_environment.get_template('provider/detail.html')
					self.response.out.write(template.render(locales))

			else:
				# We used to show a Public Profile but decided against this.
				self.redirect('/providers')

		else:
			self.redirect('/providers')

	def post(self, provider_uid):

		# Keeping all code in one handler method
		self.get(provider_uid)

class ProviderDeleteHandler(webapp2.RequestHandler):
	"""
	Handles the Authentication of the Users to the service
	We use the App Engine User Service for this.

	So it's just a redirect actually
	"""
	def get(self, provider_uid):

		provider_obj = schemas.Provider.get_by_id(int(provider_uid))

		if provider_obj is not None and provider_obj is not False:
			
			# Ok so Provider exists.
			# Now check if this is a logged in user and if they are a member of this provider.
			# If so we rather so a dashboard and edit properties and controls.
			user = users.get_current_user()
			if user:
				
				# Ok so let's check if they are a member
				membership_obj = dal.membership_by_user(provider_obj, user)
				if membership_obj is not None and membership_obj is not False:

					if provider_obj.logo:
						db.delete(provider_obj.logo)

					db.delete(dal.get_membership_ids_by_provider(provider_obj))
					provider_obj.delete()

					self.redirect('/profile')
				else:
					self.redirect('/profile')

			else:
				self.redirect('/profile')

		else:
			self.redirect('/profile')

class ProviderMemberManagerHandler(webapp2.RequestHandler):
	def post(self):
		self.redirect('/providers')

	def get(self):

		provider_obj = schemas.Provider.get_by_id(int(self.request.get('provider')))

		if provider_obj is not None and provider_obj is not False:
			
			# Ok so Provider exists.
			# Now check if this is a logged in user and if they are a member of this provider.
			# If so we rather so a dashboard and edit properties and controls.
			user = users.get_current_user()
			if user:
				
				# Ok so let's check if they are a member
				membership_obj = dal.membership_by_user(provider_obj, user)
				if membership_obj is not None and membership_obj is not False:

					# Check if we have at least one member still in the provider
					current_members = dal.memberships_by_provider(provider_obj)

					# Check for at least 1 member
					if current_members.count() > 0:

						if self.request.get('type') == 'remove':

							# Get the members to send the Mail to
							members = dal.memberships_by_provider(provider_obj)

							# Loop and Mail the Members
							for member in members:

								# Text
								text_str = str(self.request.get('email')) + ' has been removed as a member of ' + str(provider_obj.name)

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
									view='mail/provider/member_deleted.html',
									locales=template_locales)

							# Remove the Membership
							dal.delete_memberships_by_provider(provider_obj, users.User(self.request.get('email')))

						elif self.request.get('type') == 'add':

							# Get the members to send the Mail to
							members = dal.memberships_by_provider(provider_obj)

							# Loop and Mail the Members
							for member in members:

								# Text
								text_str = str(self.request.get('email')) + ' has been added as a member of ' + str(provider_obj.name)

								# Send Mail to Member
								template_locales = {
									'title': text_str,
									'description': text_str,
									'subject': text_str,
									'provider': provider_obj,
									'user': user
								}

								# The Form parameters were validated
								mailer.send(
									to=str(member.user.email()),
									reply_to='noreply@identichip.org',
									subject=template_locales['subject'],
									view='mail/new_member_just_added.html',
									locales=template_locales)

							# Send to current user
							text_str = str(provider_obj.name) + ' has added your account as a member'

							# Send Mail to Member
							template_locales = {
								'title': text_str,
								'description': text_str,
								'subject': text_str,
								'provider': provider_obj,
								'user': user
							}

							# The Form parameters were validated
							mailer.send(
								to=str(self.request.get('email')),
								reply_to='noreply@identichip.org',
								subject=template_locales['subject'],
								view='mail/newly_added_member.html',
								locales=template_locales)

							# Create new member
							membership_obj = schemas.ProviderMember(provider=provider_obj,user=users.User(self.request.get('email')))

							# Save Member
							membership_obj.put()

		self.redirect('/provider/' + str(provider_obj.key().id()) + "?section=members")