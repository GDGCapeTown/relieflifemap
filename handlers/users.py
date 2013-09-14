from google.appengine.api import users
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions

import webapp2
import jinja2

import dal


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

class ListAllowedUsers(webapp2.RequestHandler):
    def get(self):
        users = dal.get_allowed_users()

        locales = {
			'title': 'Users',
			'description': 'All Allowed Users',
			'users': users,
			'user': users.get_current_user()
        }

        template = jinja_environment.get_template('admin/users/list.html')
        self.response.out.write(template.render(locales))
