# Python Libs
import webapp2
import os
import jinja2
import os
import time

# Google Libs
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

# Custom Libs
import dal

# Set Template Folder
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

#
# Shows the stats handler
# @author Johann du Toit
#
class StatHandler(webapp2.RequestHandler):
	def get(self):

		session = dal.return_and_global_session_update(self)

		year = int(time.strftime("%Y"))

		if self.request.get('year'):
			try:
				year = int(self.request.get('year'))
			except:
				pass

		search_count = memcache.get("search_count_" + str(year))
		if search_count is None:
			search_count = db.GqlQuery("SELECT * FROM UserSearch WHERE created > DATE(:1, 1, 1) AND created < DATE(:2, 12, 31)", year, year).count()

			if not memcache.add("search_count_" + str(year), search_count, 60*10):
				pass

		success_search_count = memcache.get("success_search_count_" + str(year))
		if success_search_count is None:
			success_search_count = db.GqlQuery("SELECT * FROM UserSearch WHERE success_status = True AND created > DATE(:1, 1, 1) AND created < DATE(:2, 12, 31)", year, year).count()

			if not memcache.add("success_search_count_" + str(year), success_search_count, 60*10):
				pass

		search_contact_count = memcache.get("search_contact_count_" + str(year))
		if search_contact_count is None:
			search_contact_count = db.GqlQuery("SELECT * FROM UserSearchDetail WHERE email_sent = True AND created > DATE(:1, 1, 1) AND created < DATE(:2, 12, 31)", year, year).count()

			if not memcache.add("search_contact_count_" + str(year), search_contact_count, 60*10):
				pass

		stats = memcache.get("stat_page_" + str(year))
		if stats is None:
			stats = []

			responses = dal.get_stats({
				'year': int(year)
			})
		
			stat = {
				'year': int(year),
				'countries': dal.parse_out_countries(responses),
				'cities': dal.parse_out_cities(responses)
			}
			stats.insert(0, stat)

			if not memcache.add("stat_page_" + str(year), stats, 60*10):
				pass

		locales = {
			'title': 'Statistics',
			'description': 'Some Statistics about Searches that were performed on our website and where they came from.',
			'user': users.get_current_user(),
			'stats': stats,
			'years': xrange(2012, int(time.strftime("%Y"))+1),
			'current_year': year,
			'search_count': search_count,
			'search_contact_count': search_contact_count,
			'success_search_count': success_search_count,
			'session': session,
			'is_current_user_admin': users.is_current_user_admin()
		}
		template = jinja_environment.get_template('stats.html')
		self.response.out.write(template.render(locales))

#
# Shows the about page
# @author Johann du Toit
#
class AboutHandler(webapp2.RequestHandler):
	def get(self):

		# Create the locales
		locales = {
			'title': 'About',
			'description': 'Who we are and what we do to search all the registered providers',
			'user': users.get_current_user(),
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}

		# Parse and send template
		template = jinja_environment.get_template('about.html')
		self.response.out.write(template.render(locales))

#
# The Terms of Service to return
# @author Johann du Toit
#
class LegalTermsHandler(webapp2.RequestHandler):
	def get(self):

		# Locales
		locales = {
			'title': 'Terms of Service',
			'description': 'On what basis is this service provided. Please read this carefully.',
			'user': users.get_current_user(),
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}

		# Render and send the template
		template = jinja_environment.get_template('terms_of_service.html')
		self.response.out.write(template.render(locales))

#
# Shows the Privacy Policy
# @author Johann du Toit
#
class LegalPrivacyHandler(webapp2.RequestHandler):
	def get(self):

		# Locales
		locales = {
			'title': 'Privacy Policy',
			'description': 'How we handle data from our users and partners',
			'user': users.get_current_user(),
			'session': dal.return_and_global_session_update(self),
			'is_current_user_admin': users.is_current_user_admin()
		}

		# Parse and output template
		template = jinja_environment.get_template('privacy_statement.html')
		self.response.out.write(template.render(locales))


