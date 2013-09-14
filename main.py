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
from handlers.auth import LoginHandler, PostLoginHandler
from handlers.events import ListAPIEventsHandler, ListEventsHandler, DeleteEventsHandler, CreateEventsHandler, UpdateEventsHandler

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'secret_key_for_session_here',
}

# Register Routes
app = webapp2.WSGIApplication([

								('/', HomepageHandler),
								( '/signin', LoginHandler ),
								( '/auth', PostLoginHandler ),
								('/events.json', ListAPIEventsHandler),
								('/manage', ListEventsHandler),
								('/events/create', CreateEventsHandler),
								('/events/edit/(\d+)', UpdateEventsHandler),
								('/events/delete/(\d+)', DeleteEventsHandler)

							], debug=True, config=config)
