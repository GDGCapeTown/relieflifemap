# Python
import webapp2
import jinja2
import json
import datetime
import logging
import re
import uuid

# Our Libraries
import dal
import schemas
import runner
import counter
import mailer

# Google Apis
from google.appengine.api.logservice import logservice
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import mail
from webapp2_extras import sessions

# Configure JINJA to use our views folder as a base
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

#
# Handles showing the users the results from their search.
# Each search can contain multiple results from diffrent providers
# so we parse these from the database and show them with links
# to view the other results if their are any
# @author Johann du Toit
#
class SearchViewHandler(webapp2.RequestHandler):
	def get(self, uid, result_number=0):

		if uid:

			# Get the search object and responses
			(search_obj, search_responses) = dal.search_by_token(uid)

			# Check if the search exists and if any responses are associated with it.
			if search_obj and search_responses and search_obj.expires > datetime.datetime.now():

				# Get the current logged-in user
				user = users.get_current_user()

				# Update the expiring date. We allow anyone to view the search x minutes after it's been searched
				search_obj.expires = datetime.datetime.now() + datetime.timedelta( minutes=runner.EXPIRES_AFTER )
				search_obj.put()

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

							# Assign custom index from request
							requested_provider_uid = int(self.request.get('provider'))

							# Get the index of a the provider with that id
							current_index = [int(y.provider.key().id()) for y in success_results].index(requested_provider_uid)

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

					# Section of the Result Page to show.
					section = 'info'

					# Set section according to request
					if self.request.get('section'):

						# Parse the string as a section
						requested_section_str = str(self.request.get('section').strip().lower())

						# Is this a valid Section
						if requested_section_str in ['info', 'result', 'contact']:

							# Then we assign it
							section = requested_section_str

					# ########
					# Handle Posts if any
					# ########

					# success_message_flags
					contact_form_success = False

					# Errors
					contact_form_error = False

					# Handle Contact Form
					if self.request.POST.get('form_contact'):

						# Set section as they will want to see their response
						section = 'contact'

						# Handle the contact form
						contact_name = self.request.POST.get('form_contact_name')
						contact_email = self.request.POST.get('form_contact_email')
						contact_message = self.request.POST.get('form_contact_message')

						# Validate
						contact_form_error = None

						if single_response.email_sent == True:
							# We can't send multiple E-Mails to the same user on the same search
							contact_form_error = 'An E-Mail has already been sent to the user. We do not allow multiple E-Mails to prevent spamming. Please give the user some time to response to your E-Mail after which you\'ll be able to communicate directly.'
						elif not contact_name or len(str(contact_name).strip()) == 0:
							# Name is Required
							contact_form_error = 'Your name is Required'
						elif not contact_email or len(str(contact_email).strip()) == 0 or not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", contact_email):
							# An Valid E-Mail is Required
							contact_form_error = 'A Valid E-Mail by which the user can reach you again.'
						elif not contact_message or len(str(contact_message).strip()) == 0:
							# Message is required
							contact_form_error = 'We need a message which we will send to the user. This should include basic details such as where you found the pet and your location'
						else:

							# Generate Template to send
							template_locales = {
								'title': 'Search for #' + str(search_obj.uid),
								'description': 'Contact message by User who searched for #' + str(search_obj.uid),
								'chip': chip,
								'subject': 'Contact message by User who searched for #' + str(search_obj.uid),
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

							section = 'info'
							contact_form_success = 'true'

					# Create the Locales for the Page to use
					locales = {
						'title': 'Search for #' + str(search_obj.uid),
						'description': 'The results of the search for the Unique Number #' + str(search_obj.uid),
						'chip': chip,
						'current_response': single_response,
						'search': search_obj,
						'provider': provider,
						'success_results': search_obj.provider_success_responses,
						'failure_results': search_obj.provider_failure_responses,
						'notfound_results': search_obj.provider_notfound_responses,
						'total_providers_asked': search_obj.provider_total_requests,
						'search_obj': search_obj,
						'search_responses': search_responses,
						'search_success_responses': success_results,
						'search_failure_responses': failure_results,
						'user': user,
						'contact_form_error': contact_form_error,
						'contact_form_success': contact_form_success,
						'section': section,
						'post_params': self.request.POST,
						'contact_post_url': '/view/' + search_obj.token + "?provider=" + str(provider.key().id()) + "&response=" + str(single_response.key().id()),
						'session': dal.return_and_global_session_update(self),
						'is_current_user_admin': users.is_current_user_admin()
					}

					# Render the Template with those Values
					template = jinja_environment.get_template('search/result.html')
					self.response.out.write(template.render(locales))

				else:

					session_store = sessions.get_store(request=self.request)
					session = session_store.get_session()

					if 'search_token' not in session:
						session['search_token'] = str(uuid.uuid1())

					session_store.save_sessions(self.response)

					# Well if their was not result we redirect to homepage
					# Create the Locales for the Page to use
					locales = {
						'title': 'No Results found for #' + str(search_obj.uid),
						'description': 'The results of the search for the Unique Number #' + str(search_obj.uid),
						'success_results': search_obj.provider_success_responses,
						'failure_results': search_obj.provider_failure_responses,
						'notfound_results': search_obj.provider_notfound_responses,
						'total_providers_asked': search_obj.provider_total_requests,
						'search_obj': search_obj,
						'search': search_obj,
						'search_responses': search_responses,
						'search_success_responses': success_results,
						'search_failure_responses': failure_results,
						'user': user,
						'session': session,
						'session': dal.return_and_global_session_update(self),
						'is_current_user_admin': users.is_current_user_admin()
					}

					# self.response.out.write("<li>" + detail.provider.name + " <-> <img src=\"" + images.get_serving_url(detail.provider.logo.key(), 32) + "\" /></li>")

					# Render the Template with those Values
					template = jinja_environment.get_template('search/notfound.html')
					self.response.out.write(template.render(locales))

			else:

				# That search does not exist. Redirect them to the homepage.
				self.redirect('/')

		else:

			# They did not give a search uid redirect them to the homepage
			self.redirect('/')

	def post(self, uid):

		# Want to keep only one copy of that long code
		self.get(uid)

#
# Handles the actual searching. We have a token to limit requests from only our website.
# which ensures that this is not abused. We will later open a api with this data
# that clients can open with their keys. Which we can then limit and control.
# @author Johann du Toit
#
class SearchHandler(webapp2.RequestHandler):
	def get(self):

		# Search does not handle Post. If we got a post just take them back
		# to the homepage
		self.redirect('/')

	def post(self):

		# Check if the gave us a uid
		if self.request.get('q'):

			session_store = sessions.get_store(request=self.request)
			session = session_store.get_session()

			# Check if their token matches our
			if 'search_token' in session:

				if session['search_token'] == self.request.get('search_token'):
					del session['search_token']

					# Save the deleted token
					session_store.save_sessions(self.response)

					# Trim and check the search term. We want to avoid any errors and keep
					# it consistant for all the providers
					search_term = str(self.request.get('q')).strip().replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')

					# If the term is not a valid length we redirect the user back.
					if len(search_term) < 3:
						self.redirect('/')

					# Get all the searchable DAL's in 
					# the order that we will search them.
					providers = dal.approved_providers()

					# Run the Search Runner to request from all providers
					response = runner.search(self.request, search_term, providers)

					# Redirect to the Search's token so the user
					# can view the result. This also keeps them away from
					# executing this page multiple times as that would
					# be bad!
					self.redirect('/view/' + str(response.token))

					# Save for Stats. This is done Async
					dal.update_or_add_search_counter(self.request, response).get_result()

				else:
					# Nope so redirect them back to the hompage
					self.redirect('/')

			else:

				# Nope so redirect them back to the hompage
				self.redirect('/')

		else:

			# Nope so redirect them back to the hompage
			self.redirect('/')


