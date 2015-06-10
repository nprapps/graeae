#!/usr/bin/env python
"""
Example application views.

Note that `render_template` is wrapped with `make_response` in all application
routes. While not necessary for most Flask apps, it is required in the
App Template for static publishing.
"""

import app_config
import csv
import json
import oauth
import static

from flask import Flask, make_response, render_template
from render_utils import make_context, smarty_filter, urlencode_filter, format_commas_filter
from werkzeug.debug import DebuggedApplication

app = Flask(__name__)
app.debug = app_config.DEBUG

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')
app.add_template_filter(format_commas_filter, name='format_commas')

@app.route('/')
@oauth.oauth_required
def index():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    context = make_context()

    context['facebook_metrics'] = (
        ('likes', 'Likes'),
        ('shares', 'Shares'),
        ('comments', 'Comments'),
        ('link_clicks', 'Link clicks'),
    )

    with open('www/live-data/insights_summary.csv') as f:
        reader = csv.DictReader(f)
        context['insights_summary'] = list(reader)

    with open('www/live-data/homepage_summary.csv') as f:
        reader = csv.DictReader(f)
        context['homepage_summary'] = list(reader)

    with open('www/live-data/contribution_summary.csv') as f:
        reader = csv.DictReader(f)
        context['contribution_summary'] = list(reader)

    return make_response(render_template('index.html', **context))

app.register_blueprint(static.static)
app.register_blueprint(oauth.oauth)

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab app" instead!'
