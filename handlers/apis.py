# Python Apis
import webapp2
import jinja2
import os
import hashlib
from datetime import date
import datetime
import time
import json

# Google Apis
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import memcache

# Custom
import schemas
import dal
import runner
import mailer

#
# Authenticates the Client and returns the client object. Else a false.
# @author Johann du Toit
#
def authenticate_client(token):

	# Check for the client
	client_obj = dal.client_by_token(token)

	# Check if a client was given
	if client_obj:
		return client_obj
	else:
		# Else we return false!
		return False

#
# Allows Clients to Contact the Owner without us ever giving out the contact information.
# They are only allowed to send the E-Mail once !
# @author Johann du Toit
#
class ApiContactHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(json.dumps({
			'error': 'Method only supports post'
		}))

	def post(self):

		# Check if they gave a token
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Check client
			if client_obj and client_obj is not False:

				# Well get the details
				# http://www.identichip.org/apis/v1/contact?token=testing&key=ag5kZXZ-aWRlbnRpY2hpcHIQCxIKVXNlclNlYXJjaBhwDA&option=ag5kZXZ-aWRlbnRpY2hpcHIWCxIQVXNlclNlYXJjaERldGFpbBhxDA
				
				if self.request.get('key'):

					# Get the search object and responses
					(search_obj, search_responses) = dal.search_by_token(self.request.get('key'))

					# Check if the search exists and if any responses are associated with it.
					if search_obj and search_responses and search_obj.expires > datetime.datetime.now():

						# Filter the Results to what we need
						success_results = []
						failure_results = []

						for response in search_responses:

							if response.status == runner.ProviderResponse.STATUS_FOUND:
								success_results.append(response)
							elif response.status not in [runner.ProviderResponse.STATUS_FOUND, runner.ProviderResponse.STATUS_NOTFOUND]:
								failure_results.append(response)

						# Get the current provider, chip and owner to show
						if len(success_results) > 0:
						
							# What response should we look at ?
							current_index = 0

							if self.request.get('provider'):

								# Only executed if the user provided a provider to check for.
								# This is used when multiple provider gave a response.
								# So we can list all the responses for the user.
								try:

									# Get the index of a the provider with that id
									current_index = [y.provider.key() for y in success_results].index(str(self.request.get('provider')))

								except Exception as ex:

									# Just use the default value
									current_index = 0

							# Check that the index is sane else we make it the first one
							if current_index > (len(success_results)):
								current_index = 0

							# Single Response Object
							single_response = success_results[current_index]

							# Get the provider
							provider = success_results[current_index].provider

							# Get the Chip Details
							chip = json.loads(success_results[current_index].parsed_response)

							# Handle the contact form
							contact_name = self.request.POST.get('contact_name')
							contact_email = self.request.POST.get('contact_email')
							contact_message = self.request.POST.get('contact_message')

							if single_response.email_sent == True:

								# We can't send multiple E-Mails to the same user on the same search
								self.response.out.write(json.dumps({
									'error': 'An E-Mail has already been sent to the user. We do not allow multiple E-Mails to prevent spamming. Please give the user some time to response to your E-Mail after which you\'ll be able to communicate directly.'
								}))
								
							elif not contact_name or len(str(contact_name).strip()) == 0:
								# Name is Required
								self.response.out.write(json.dumps({
									'error': 'The Name of the person that wants to send the Mail is required'
								}))
							elif not contact_email or len(str(contact_email).strip()) == 0 or not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", contact_email):
								# An Valid E-Mail is Required
								self.response.out.write(json.dumps({
									'error': 'The Valid E-Mail of the user is required. This must match our pattern!'
								}))
							elif not contact_message or len(str(contact_message).strip()) == 0:
								# Message is required
								self.response.out.write(json.dumps({
									'error': 'We need a message which we will send to the user. This should include basic details such as where the user found the pet and their location or some arrange to call them.'
								}))
							else:

								# Generate Template to send
								template_locales = {
									'chip': chip,
									'subject': 'Contact message by User who searched for #' + str(chip.uid),
									'sender_name': str(contact_name).strip(),
									'sender_email': str(contact_email).strip(),
									'message': str(contact_message).strip(),
									'provider': provider
								}

								# The Form parameters were validated
								mailer.send(
									to=str(chip['owner']['email']),
									reply_to=str(template_locales['sender_email']),
									subject=str(template_locales['subject']),
									view='mail/contact_from_search.html',
									locales=template_locales)

								# Update to show that the E-Mail was sent
								single_response.email_sent = True
								single_response.email_sent_from = str(contact_email).strip()
								single_response.email_sent_name = str(contact_name).strip()
								single_response.email_sent_text = str(contact_message).strip()
								single_response.put()

								self.response.out.write(json.dumps({
									'message': 'Success E-Mail was sent !',
									'status': True
								}))

						else:

							# This was not a succesfull search !
							self.response.out.write(json.dumps({
									'error': 'This was not a succesfull search.'
								}))

					else:

						# Search not found or expired
						self.response.out.write(json.dumps({
								'error': 'Either your search could not be found or it has expired. Searches are only valid for ' + str(runner.EXPIRES_AFTER) + ' minutes after their last action'
							}))

				else:

					# 
					self.response.out.write(json.dumps({
								'error': 'No Search Key Provided'
							}))

			else:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

		else:
			# Inform them
			self.response.out.write(json.dumps({
					'error': 'No Client token was given. Please login and create a client to start searching from our providers'
				}))

#
# The API Search Handler. This is the handler that handles call to the API to do a search
# @author Johann du Toit
#
class ApiSearchHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(json.dumps({
			'error': 'Method only supports post'
		}))

	def post(self):

		# Check if they gave a token
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Check client
			if client_obj and client_obj is not False:

				# Found the client. Now check if they are still in their dails quota !
				# We only allow as many results as assigned to the client. 
				# We want the option to change this value for certain users that have
				# big volume sites. if the count is 0 that means we allow unlimited calls.
				# We allow 0 clients as our site uses this api too for the javascript calls

				# Get the current date and year
				current_date = int(time.strftime("%d"))
				current_month = int(time.strftime("%m"))
				current_year = int(time.strftime("%Y"))

				# get the calls
				search_apis_calls = dal.search_api_calls(client_obj, current_date, current_month, current_year)
				
				# Local Var with Limit
				daily_limit_local = search_apis_calls.count()

				# If the count of calls bigger than 0
				if search_apis_calls is not False and ( client_obj.daily_limit == 0 or daily_limit_local < client_obj.daily_limit ):

					# Check if the Q parameter was given for a search
					if self.request.get('q') and len(self.request.get('q')) >= 3:

						# Well let's do some searches !
						# Trim and check the search term. We want to avoid any errors and keep
						# it consistant for all the providers
						search_term = str(self.request.get('q')).strip().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')

						# Insert info about the call
						inserted_call = {}

						# Get all the searchable DAL's in 
						# the order that we will search them.
						providers = dal.approved_providers()

						# Run the Search Runner to request from all providers
						search_raw_response = runner.search(self.request, search_term, providers)

						# Results
						# We just show quick info. Such as name, pic and some basic info.
						# If the user wants to send a E-Mail they can do so with the specified contact url.
						# This is to protected the E-Mail of address of the owner.
						(search_obj, search_responses) = dal.search_by_token(str(search_raw_response.token))

						# Make the result text
						result_text = 'notfound'

						# Check if the response was a success
						if search_obj.provider_success_responses > 0:
							result_text = 'found'

						# Create the results
						success_results = []
						failure_results = []

						# Loop and add the diffrent results
						for response in search_responses:

							# Create the Provider Obj
							provider_obj = {}
							provider_obj['id'] = response.provider.key().id()
							provider_obj['name'] = response.provider.name
							provider_obj['website'] = response.provider.website
							provider_obj['logo'] = response.provider.logo_url(128)

							if response.status == runner.ProviderResponse.STATUS_FOUND:

								# Parse to get details
								data = res = json.loads(response.parsed_response)

								# Assign params
								res['owner_name'] = data['owner']['name']
								res['contact_url'] = 'http://www.identichip.org/apis/v1/contact?token=' + str(self.request.get('token')) + "&key=" + str(search_obj.token) + "&provider=" + str(response.provider.key())

								# Remove owner details
								del res['owner']

								# Assign provider params
								res['provider'] = provider_obj

								# Add to list
								success_results.append(res)

							elif response.status not in [runner.ProviderResponse.STATUS_FOUND, runner.ProviderResponse.STATUS_NOTFOUND]:
								
								# Add the failed provider
								failure_results.append(provider_obj)

						# Well we just added a count
						daily_limit_local += 1

						# Redirect to the Search's token so the user
						# can view the result. This also keeps them away from
						# executing this page multiple times as that would
						# be bad!
						self.response.out.write(json.dumps({
								'result': result_text,
								'token': str(search_obj.token),
								'url': 'http://www.identichip.org/view/' + str(search_obj.token),
								'success': success_results,
								'failed': failure_results,
								'daily_limit': client_obj.daily_limit,
								'remaining_limit': int(client_obj.daily_limit) - daily_limit_local
							}))

						# Save client call
						client_call = schemas.APICallCount()
						client_call.date = current_date
						client_call.month = current_month
						client_call.year = current_year
						client_call.uid = search_term
						client_call.client = client_obj
						client_call.search = search_obj
						db.put_async(client_call).get_result()

						# Save for Stats. This is done Async. This is the global search stat
						dal.update_or_add_search_counter(self.request, search_raw_response).get_result()

					else:

						# No UID to search ???
						self.response.out.write(json.dumps({
							'error': 'No q parameter was given ! This parameter tells us what UID to search for. Which is quite imporant ... Please see the developer documentation for this at http://www.identichip.org/developer'
						}))

				else:

					# Inform them
					self.response.out.write(json.dumps({
							'error': 'This Token has exceeded it\'s daily call limit of ' + str(client_obj.daily_limit) + ". If your client requires more please get in contract with us as we can arrange custom plans."
						}))

			else:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

		else:
			# Inform them
			self.response.out.write(json.dumps({
					'error': 'No Client token was given. Please login and create a client to start searching from our providers'
				}))

#
# The Provider Search Details handler. With this Handler Providers clients can return 
# information about searches from the provider. With the most important being the ability
# to see searches for specified UID. So users from the provider can see if their microchip / tag
# has been searched for some time. Useful when user from the provider would like to see
# if a pet has been searched for.
#
# Remember this api method return information about searches and that's what it's intended for !
# To get stats use the stats endpoint. Which is available to all !
#
# @author Johann du Toit
#
class ApiSearchDetailHandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write(json.dumps({
			'error': 'Method only supports post'
		}))

	def post(self):

		# Check if they gave a token
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Check client
			if client_obj and client_obj is not False:

				# Check if the client belongs to a provider.
				if client_obj.provider:

					# Defaults
					uid = None
					limit = 10
					skip = 0 * limit

					# Set from Query String
					if self.request.get('uid'):
						uid = str(self.request.get('uid')).strip().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')

					if self.request.get('limit'):
						try:

							limit = int(self.request.get('limit'))

							if limit > 25:
								limit = 10

						except:
							# Just set back to default
							limit = 10

					if self.request.get('offset'):
						try:

							skip = int(self.request.get('offset'))

						except:
							# Just set back to default
							skip = 0

					# Get the searches from database
					if uid:
						# For a UID
						(searches_from_db_count, searches_from_db)  = dal.searches_for_specified_uid(client_obj.provider, uid, limit, skip)
					else:
						# Just all the latest searches
						(searches_from_db_count, searches_from_db)  = dal.searches_for_provider(client_obj.provider, limit, skip)

					# The results to return
					results = []

					# Loop the results and create the output
					for search_detail_obj in searches_from_db:

						# Output Object
						output_obj = {}

						# Create Obj with Params
						output_obj['uid'] = search_detail_obj.uid

						# Locally these values are not populated ...
						output_obj['country'] = getattr(search_detail_obj.search, 'country', 'za')
						output_obj['region'] = getattr(search_detail_obj.search, 'region', 'wc')
						output_obj['city'] = getattr(search_detail_obj.search, 'city', 'stellenbosch')
						# Locally these values are not populated ...

						if search_detail_obj.search.user and search_detail_obj.search.user is not None:
							output_obj['user'] = search_detail_obj.search.user.email()
						else:
							output_obj['user'] = None

						output_obj['datetime_searched'] = search_detail_obj.search.created.isoformat()
						output_obj['email'] = {
							'sent': search_detail_obj.email_sent
						}

						if search_detail_obj.email_sent:

							# Add the EMail Details
							output_obj['email']['mail'] = search_detail_obj.email_sent_from
							output_obj['email']['name'] = search_detail_obj.email_sent_name
							output_obj['email']['message'] = search_detail_obj.email_sent_text

						# Add to list

						results.append(output_obj)

					# Return the results
					self.response.out.write(json.dumps({
							'count': searches_from_db_count,
							'offset': skip,
							'limit': limit,
							'items': results
						}))

				else:
					# Inform them
					self.response.out.write(json.dumps({
							'error': 'Only Clients that belong to a provider may use this endpoint. The enpoint serves as a way for providers to pull information of searches that have taken place in the system.'
						}))

			else:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

		else:
			# Inform them
			self.response.out.write(json.dumps({
					'error': 'No Client token was given. Please login and create a client to start searching from our providers'
				}))

#
# Lists all the Providers currently on the system that are tested and approved !
# @author Johann du Toit
#
class ApisProviderListHandler(webapp2.RequestHandler):
	"""
	Lists all Providers for the public.

	The page they will view to see all our registerd providers
	"""
	def get(self):

		# Get the current logged-in user
		user = users.get_current_user()

		# List all approved providers for use by others
		providers = dal.approved_providers()

		# Expose as JSON
		output_obj = []

		for provider in providers:
			provider_obj = {
				'id': provider.key().id(),
				'name': provider.name,
				'website': provider.website,
				'logo': provider.logo_url(128)
			}

			provider_obj['website'] = provider.website

			output_obj.append(provider_obj)

		# Output as JSON
		self.response.out.write(json.dumps(output_obj))

#
# Builds a list of parameters that we use in our searches
# @author Johann du Toit
#
def build_search_params(client_obj, request):

	# THe Params and any errors we found
	params = {}
	errors = []

	# Check for country ?
	if request.get('country'):
		params["country"] = request.get('country')

	# Check for city ?
	if request.get('city'):
		params["city"] = request.get('city')

	# Check for this year
	if request.get('year'):
		try:
			params["year"] = int(request.get('year'))
		except:
			errors.append('Year must be a Number!')
	else:
		params["year"] = time.strftime("%Y")

	# Check for a week ?
	if request.get('week'):
		try:
			params["week"] = int(request.get('week'))
		except:
			errors.append('Week must be a Number!')

	# Check only for a certain provider ?
	if request.get('provider'):

		# Check CLient
		if client_obj:
			params["provider"] = client_obj.provider
		else:
			errors.append('Must be authenticated with a client from the provider to list the stats from that provider')

	# Return the results
	return (params, errors)

#
# Lists global stats
# @author Johann du Toit
#
class ApisStatsHandler(webapp2.RequestHandler):

	def get(self):

		# Get the Client for stats on a provider
		client_obj = False

		# Do the authentication
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Well was it valid ?
			if client_obj is False:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

				# Stop the request
				return

		# Build our params or errors
		(params, errors) = build_search_params(client_obj, self.request)

		# Create the output Object
		output = {}

		# Go through each month in the year
		for year in xrange(2012, int(time.strftime("%Y"))+1):

			# Set current year
			params.year = int(year)

			# Get the stats
			responses = dal.get_stats(params)

			# List of weeks
			weeks = []

			# Look each week in this month !
			for week in dal.parse_out_weeks(year, responses):
				weeks.append(int(week['found']))

			# Add Values to single looping value
			output[str(year)] = dal.parse_out_general_count(responses)
			output[str(year)]["weeks"] = weeks

		# Output to response
		self.response.out.write(json.dumps(output))

#
# Ouputs Stats according to Country.
# @author Johann du Toit
#
class ApisCountryStatsHandler(webapp2.RequestHandler):

	def get(self):

		# Get the Client for stats on a provider
		client_obj = False

		# Do the authentication
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Well was it valid ?
			if client_obj is False:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

				# Stop the request
				return

		# Build our params or errors
		(params, errors) = build_search_params(client_obj, self.request)

		# Check if there was any errors
		if len(errors) > 0:
			self.response.out.write(json.dumps({ 'errors': errors }))
		else:

			# Object to return
			stats = {}

			# Get the RAW responses from DB.
			responses = dal.get_stats(params)

			# Object to return
			stats = {}

			# Parse out Countries
			country_response = dal.parse_out_countries(responses)
			for country_code in country_response:

				# If found is there
				if 'found' in country_response[country_code]:
					stats[str(country_code)]  = int(country_response[country_code]["found"])
				else:
					stats[str(country_code)]  = 0
			
			# Output that list !
			self.response.out.write(json.dumps(stats))

#
# Lists a city view of our filtered stats
# @author Johann du Toit
#
class ApisCityStatsHandler(webapp2.RequestHandler):
	def get(self):

		# Get the Client for stats on a provider
		client_obj = False

		# Do the authentication
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Well was it valid ?
			if client_obj is False:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

				# Stop the request
				return

		# Build our params or errors
		(params, errors) = build_search_params(client_obj, self.request)

		# Did we get any errors ?
		if len(errors) > 0:
			self.response.out.write(json.dumps({ 'errors': errors }))
		else:

			# Get our responses
			responses = dal.get_stats(params)

			# Our stat output object to return
			stats = {}

			# Parse the City out 
			city_response = dal.parse_out_cities(responses)
			for city_code in city_response:

				# Get Response
				if 'found' in city_response[city_code]:
					stats[str(city_code)] = int(city_response[city_code]["found"])
				else:
					stats[str(city_code)] = 0
			
			# Write our Output
			self.response.out.write(json.dumps(stats))

#
# Returns a List of all the E-Mails of providers in the system.
# @author Johann du Toit
#
class MemberAPIListHandler(webapp2.RequestHandler):
	def get(self):

		# Check if they gave a token
		if self.request.get('token'):

			# They did so now let's check the client
			client_obj = authenticate_client(str(self.request.get('token')))

			# Check client
			if client_obj and client_obj is not False:

				if client_obj.allowed_provider_member_emails and client_obj.allowed_provider_member_emails == True:

					output = []
					already_in = []
					members = schemas.ProviderMember.all()
					for member in members:
						if str(member.user.email()) not in already_in:

							output.append({
									'email': str(member.user.email()),
									'providers': [
										{
											'name': str(member.provider.name),
											'website': str(member.provider.website),
											'logo': member.provider.logo_url(128)
										}
									]
								})

							already_in.append(str(member.user.email()))

						else:

							# Add this provider if not present in user list yet.
							for member_detail in output:

								# If member
								if member_detail['email'] == str(member.user.email()):

									# Add Provider
									member_detail["providers"].append({
											'name': str(member.provider.name),
											'website': str(member.provider.website),
											'logo': member.provider.logo_url(128)
										})

					self.response.out.write(json.dumps(output))

				else:
					# Inform them
					self.response.out.write(json.dumps({
							'error': 'Only Approved Clients may get the Addresses of Members'
						}))

			else:
				# Inform them
				self.response.out.write(json.dumps({
						'error': 'No such client found. Invalid Token !'
					}))

		else:
			# Inform them
			self.response.out.write(json.dumps({
					'error': 'No Client token was given. Please login and create a client to start searching from our providers'
				}))

