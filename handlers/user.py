# Python Lib
import webapp2
import jinja2
import os
import logging
import json
import io
import urllib
import urllib2

# Google Lib
from google.appengine.api import users
from google.appengine.api.logservice import logservice
from google.appengine.api import oauth
from webapp2_extras import sessions
from google.appengine.api import urlfetch

# Custom Lib
import dal

# Setup our View Environment
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

# Read Settings file
settings = json.load(open('settings.json'))

# OAuth Values
INIT = {
	'APP_NAME': str(settings['app_name']),
	'SCOPES': ['https://www.google.com/m8/feeds/', 'https://apps-apis.google.com/a/feeds', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/apps.groups.settings'],
	'SECRET': str(settings['secret']),
	'KEY': str(settings['key'])
}

#
# The Profile Page of the user. From here we initially show all their searches
# They can then navigate to handle other areas of their account. Such as providers
# where they view or create a provider.
# @author Johann du Toit
#
class ProfileHandler(webapp2.RequestHandler):
	"""
	Handles the Authentication of the Users to the service
	We use the App Engine User Service for this.

	So it's just a redirect actually
	"""
	def get(self):

		# Get the user
		user = users.get_current_user()

		# Check if the user is logged-in
		if user:
			
			# Lists from DAL
			providers = dal.providers_by_user(user)
			clients = dal.get_clients_by_user(user)
			searches = dal.get_user_searches(user, 5, 2)

			# Locales of the Template
			locales = {
				'title': user.nickname(),
				'description': 'Search Microchips',
				'user': user,
				'providers': providers,
				'provider_count': len(providers),
				'clients': clients,
				'client_count': clients.count(),
				'searches': searches,
				'search_count': len(searches),
				'session': dal.return_and_global_session_update(self),
				'is_current_user_admin': users.is_current_user_admin()
			}

			# Create our template
			template = jinja_environment.get_template('user/profile.html')

			# Render Template
			self.response.out.write(template.render(locales))

		else:
			# Redirect to login
			self.redirect('/signin')

class ConnectHandler(webapp2.RequestHandler):
	"""
	Handles the Authentication of the Users to the service
	We use the App Engine User Service for this.

	So it's just a redirect actually
	"""
	def get(self):

		# Normal Google User Account
		self.redirect(users.create_login_url('/auth'))

#
# Logs users out and redirects them back to the frontpage.
# @author Johann du Toit
#
class LogoutHandler(webapp2.RequestHandler):
	def get(self):

		# Logout and Redirect
		self.redirect(users.create_logout_url("/"))

#
# Parse the Contacts Response
# @author Johann du Toit
#
def parse_contacts(json_body_string):

	# List
	contacts = []

	# Parse JSON
	token_response = json.loads(json_body_string)

	# Check
	if 'entry' in token_response["feed"]:

		# Parse and loop contacts
		for entry_obj in token_response["feed"]["entry"]:

			# Sanity Check
			if 'gd$email' in entry_obj:

				# For each mail add the contact
				for mail_obj in entry_obj["gd$email"]:

					# Add Contact
					contact_obj = {}

					# Set Param
					contact_obj["id"] = entry_obj["id"]["$t"]
					contact_obj["email"] = mail_obj["address"]

					# Only Name is it's included
					if 'title' in entry_obj and '$t' in entry_obj['title'] and len(str(entry_obj["title"]["$t"])) > 0:
						contact_obj["name"] = entry_obj["title"]["$t"]

					# Append Contact
					contacts.append(contact_obj)

	# Return Contacts
	return contacts

#
# Parse the Members Response
# @author Johann du Toit
#
def parse_members(json_body_string):

	# List
	contacts = []

	# Parse JSON
	token_response = json.loads(json_body_string)

	# Check
	if 'entry' in token_response["feed"]:
		
		# Parse and loop contacts
		for entry_obj in token_response["feed"]["entry"]:

			# Sanity Check
			if 'apps$login' in entry_obj:

				# For each mail add the contact
				login_obj = entry_obj["apps$login"]
				name_obj = entry_obj["apps$name"]

				# Add Contact
				contact_obj = {}

				# Set Param
				contact_obj["id"] = entry_obj["id"]["$t"]
				contact_obj["email"] = login_obj["userName"] + '@' + os.environ['USER_ORGANIZATION']

				# Only Name is it's included
				contact_obj["name"] = name_obj["givenName"] + ' ' + name_obj["familyName"]

				# Append Contact
				contacts.append(contact_obj)

	# Return Contacts
	return contacts

#
# User List API Endpoint. Used when adding members.
# This is used for the super bar.
# We pull contacts and users from the domain
# @author Johann du Toit
#
class ContactingListUserHandler(webapp2.RequestHandler):
	def get(self):

		# Get the session store and session
		session_store = sessions.get_store(request=self.request)

		# Get the Current Session
		session = session_store.get_session()

		# Contacts
		contacts = []

		# Is contact in IF
		if session and 'contacts' in session:

			# Output Session info
			self.response.out.write(json.dumps(session['contacts']))

		# Check Session Variables
		elif session and 'access_token' in session:

			# Do a async http fetch
			rpcs = []

			# Q String
			q_str = str(self.request.get('term')).lower()

			# Url
			contacts_url_str = 'https://www.google.com/m8/feeds/contacts/default/full?alt=json&updated-min=2007-03-16T00:00:00&max-results=1000&q=' + q_str

			# Create the RPC
			contacts_rpc = urlfetch.create_rpc(10)
			contacts_rpc.type = 'contacts'
			urlfetch.make_fetch_call(rpc=contacts_rpc, url=contacts_url_str,method=urlfetch.GET,headers={'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'OAuth ' + str(session['access_token'])})
			rpcs.append(contacts_rpc)

			# Check to add domain users add
			if 'USER_ORGANIZATION' in os.environ and len(os.environ['USER_ORGANIZATION']) > 0:

				# Url to assign
				members_url_str = 'https://apps-apis.google.com/a/feeds/' + os.environ['USER_ORGANIZATION'] + '/user/2.0?alt=json'

				# Add RPC to list members
				members_rpc = urlfetch.create_rpc(10)
				members_rpc.type = 'members'
				urlfetch.make_fetch_call(rpc=members_rpc, url=members_url_str,method=urlfetch.GET,headers={'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'OAuth ' + str(session['access_token'])})
				rpcs.append(members_rpc)

			# Parse all the RPC handlers
			for rpc in rpcs:

				# Wait for the HTTP client response and get the content
				content_str = rpc.get_result().content

				# Parse out
				if rpc.type == 'contacts':

					# Parse the JSON String that was received from the Provider.
					for contact in parse_contacts(content_str):

						# Add contact
						contacts.append(contact)

				# Parse out users
				elif rpc.type == 'members':

					# Parse the JSON String that was received from the Provider.
					for contact in parse_members(content_str):

						# Add contact
						contacts.append(contact)
			
			# Do some filtering
			if self.request.get('term') and len(self.request.get('term')) > 0:

				# Lists
				filtered_lists = []

				# Get term
				term_str = str(self.request.get('term')).lower()

				# Loop and filter
				for contact in contacts:

					# Check
					if ('name' in contact and term_str in contact['name'].lower()) or ('email' in contact and term_str in contact['email'].lower()):

						# Add and then write
						filtered_lists.append(contact)

				# Output contacts
				self.response.out.write(json.dumps(filtered_lists[:10]))

			else:

				# Output contacts
				self.response.out.write(json.dumps(contacts[:10]))
				

		else:

			# Something went wrong
			output = {
				'error': 'Something went wrong while getting the user lists',
				'type': 'general'
			}

			# Output
			self.response.out.write(json.dumps(output))

#
# Redirects to the OAuth Dialog
# @author Johann du Toit
#
class AuthHandler(webapp2.RequestHandler):
	def get(self):

		# Normal Google User Account
		self.redirect('https://accounts.google.com/o/oauth2/auth?redirect_uri=http://www.identichip.org/auth/callback&response_type=code&client_id=' + str(INIT['KEY']) + '&approval_prompt=auto&scope=' + ' '.join(INIT["SCOPES"]) + '&access_type=offline')

#
# Callback from Google
# @author Johann du Toit
#
class AuthCallbackHandler(webapp2.RequestHandler):
	def get(self):

		# Check of code
		if self.request.get('code') and not self.request.get('error'):

			# Code String
			code_str = self.request.get('code')

			# Get the String
			url = "https://accounts.google.com/o/oauth2/token"

			form_fields = {
				"code": str(code_str),
				"client_id": str(INIT['KEY']),
				"client_secret": str(INIT['SECRET']),
				"redirect_uri": "http://www.identichip.org/auth/callback",
				"grant_type": "authorization_code",
			}
			
			# Create Post Request to send and get data from
			form_data = urllib.urlencode(form_fields)
			result = urlfetch.fetch(url=url,payload=form_data,method=urlfetch.POST,headers={'Content-Type': 'application/x-www-form-urlencoded'})

			if result.status_code == 200:

				# Get Content
				content_str = result.content

				# Parse JSON
				token_response = json.loads(content_str)
				
				# Get the session store and session
				session_store = sessions.get_store(request=self.request)

				# Get the Current Session
				session = session_store.get_session()

				# Check if token in the session
				session['access_token'] = str(token_response["access_token"])

				# Save the session
				session_store.save_sessions(self.response)

				# Redirect to profile
				self.redirect('/profile')

			else:

				# Start Auth Again
				self.redirect('/auth')

		else:

			# Redirect to auth
			self.redirect('/auth')