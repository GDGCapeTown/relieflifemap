import datetime
import webapp2
import jinja2
import dal
import schemas

from google.appengine.api import users
from google.appengine.api.logservice import logservice
from webapp2_extras import sessions


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

class ListUserHandler(webapp2.RequestHandler):
    def get(self):
        user_objs = dal.get_allowed_users()

        print len(user_objs)

        locales = {
			'title': 'Users',
			'description': 'All Allowed Users',
			'users': user_objs,
			'user': users.get_current_user()
        }

        template = jinja_environment.get_template('admin/list_users.html')
        self.response.out.write(template.render(locales))


class CreateUserHandler(webapp2.RequestHandler):
    def post(self):
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

        user = schemas.AllowedUser.get_by_id(int(user_uid))
        if user:
            user.delete()

        self.redirect('/users')
