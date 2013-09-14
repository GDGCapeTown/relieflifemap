# Python
import webapp2
import jinja2
import json
import datetime
import logging
import re
import uuid
import io

# Our Libraries
import dal
import schemas
import runner
import counter

# Google Apis
from google.appengine.api.logservice import logservice
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import mail
from webapp2_extras import sessions

# Configure JINJA to use our views folder as a base
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader('views'))

# Read Settings file
settings = json.load(open('settings.json'))

#
# Generic Send Function used by the site.
# @author Johann du Toit
#
def send(to, reply_to, subject, view, locales):

	# Get the Template
	email_template = jinja_environment.get_template(view)

	# Render the Template
	email_template_content = email_template.render(locales)

	# The Form parameters were validated
	mail.send_mail(sender=str(settings['from_mail_addr']),
		reply_to=str(reply_to),
		to=str(to),
		subject=str(subject),
		body=email_template_content,
		html=email_template_content)

#
# Function to Send Templated Mail to all admins of the App Engine App
# @author Johann du Toit
#
def send_admin(subject, body):

	# The Form parameters were validated
	mail.send_mail_to_admins(sender=str(settings['from_mail_addr']),
		subject=str(subject),
		body=str(body))