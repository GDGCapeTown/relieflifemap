#!/usr/bin/env python

# Python Libs
import webapp2
import jinja2
import os
import urllib

# Google Libs
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users

# Custom Libs
import schemas as schema
import dal

# Setup the Handlers
from handlers.homepage import HomepageHandler
from handlers.auth import LoginHandler, PostLoginHandler, FailedLoginHandler, LogoutHandler
from handlers.events import ListAPIEventsHandler, ListAllAPIEventsHandler, ListEventsHandler, DeleteEventsHandler, SaveEventsHandler, DisableEventsHandler
from handlers.users import ListUserHandler, CreateUserHandler, DeleteUserHandler, ListAPIUserHandler

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'secret_key_for_session_here',
}

# Register Routes
app = webapp2.WSGIApplication([

								('/', HomepageHandler),
								( '/signin', LoginHandler ),
								( '/logout', LogoutHandler ),
								( '/auth', PostLoginHandler ),
								('/events.json', ListAPIEventsHandler),
								('/allevents.json', ListAllAPIEventsHandler),
								( '/authfailed', FailedLoginHandler ),
								('/manage', ListEventsHandler),
								('/events/disable/(\d+)', DisableEventsHandler),
								('/events/save', SaveEventsHandler),
								('/events/delete/(\d+)', DeleteEventsHandler),
								('/users.json', ListAPIUserHandler),
                                ('/users', ListUserHandler),
                                ('/users/create', CreateUserHandler),
                                ('/users/delete/(\d+)', DeleteUserHandler),

							], debug=True, config=config)
