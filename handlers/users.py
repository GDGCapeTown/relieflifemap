import datetime
import webapp2
import jinja2
import dal
import schemas
import json

from google.appengine.api import users
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

class ListUserHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		user_objs = dal.get_allowed_users()

		locales = {
			'title': 'Users',
			'description': 'All Allowed Users',
			'users': user_objs,
			'user': users.get_current_user()
		}

		template = jinja_environment.get_template('admin/list_users.html')
		self.response.out.write(template.render(locales))

class ListAPIUserHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		user_objs = dal.get_allowed_users()

		output_event = []
		already_in = []

		try:
			# Iterate over the users in the results
			for user in user_objs:
					  output_event.append( {
							'id': user.key().id(),
							'name': user.name,
							'email': user.email,
						} )

		except search.Error:
			print logging.exception('get users failed')


		self.response.out.write(json.dumps(output_event))


class CreateUserHandler(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		now = datetime.datetime.now()
		data = {
			'name': str(self.request.POST.get('name')).strip(),
			'email': str(self.request.POST.get('email')).strip(),
			'created': now,
			'lastupdated': now,
		}

		user = schemas.AllowedUser(**data)
		user.put()

		self.redirect('/users')


class DeleteUserHandler(webapp2.RequestHandler):
	def get(self, user_uid):

		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))

		user = schemas.AllowedUser.get_by_id(int(user_uid))
		if user:
			user.delete()

		self.redirect('/users')
