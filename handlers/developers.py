# Python Libs
import webapp2
import os
import jinja2
import os
import time

# Google Libs
from google.appengine.api import users
from google.appengine.api import memcache

# Custom Libs
import dal

# Set Template Folder
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

#
# Shows the developer guide
# @author Johann du Toit
#
class DeveloperHandler(webapp2.RequestHandler):
	def get(self):
		locales = {
			'title': 'Developer Documentation',
			'description': 'Documentation on how to build your own provider',
			'user': users.get_current_user(),
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('developer/about.html')
		self.response.out.write(template.render(locales))

#
# Shows the developer guide
# @author Johann du Toit
#
class DeveloperSearchHandler(webapp2.RequestHandler):
	def get(self):
		locales = {
			'title': 'Searching with our API',
			'description': 'Learn how to use our API to include searching in your Application',
			'user': users.get_current_user(),
			'section': 'search',
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('developer/search.html')
		self.response.out.write(template.render(locales))

#
# Shows the developer guide
# @author Johann du Toit
#
class DeveloperSearchDetailsHandler(webapp2.RequestHandler):
	def get(self):
		locales = {
			'title': 'Details on Searches',
			'description': 'Get Details on searches that occured for your Provider',
			'user': users.get_current_user(),
			'section': 'details',
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('developer/details.html')
		self.response.out.write(template.render(locales))

#
# Stats Docs for the Apis
# @author Johann du Toit
#
class DeveloperStatsHandler(webapp2.RequestHandler):
	def get(self):
		locales = {
			'title': 'Search Statistics API',
			'description': 'Get the API',
			'user': users.get_current_user(),
			'section': 'stats',
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('developer/stats.html')
		self.response.out.write(template.render(locales))
#
# Docs to list all providers in the system
# @author Johann du Toit
#
class DeveloperProvidersHandler(webapp2.RequestHandler):
	def get(self):
		locales = {
			'title': 'List of Providers',
			'description': 'Get the API',
			'user': users.get_current_user(),
			'section': 'listing',
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('developer/providers.html')
		self.response.out.write(template.render(locales))
#
# Docs to list all providers in the system
# @author Johann du Toit
#
class DeveloperEndpointHandler(webapp2.RequestHandler):
	def get(self):
		locales = {
			'title': 'Creating a Provider Endpoint',
			'description': 'Get the API',
			'user': users.get_current_user(),
			'section': 'endpoint',
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('developer/endpoint.html')
		self.response.out.write(template.render(locales))



