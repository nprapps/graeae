#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
import app_config
import dataset
import logging
import requests

from dateutil import parser
from fabric.api import local, task
from facebook import GraphAPI

SECRETS = app_config.get_secrets()
FACEBOOK_USER = 'NPR'

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@task
def local_bootstrap():
    local('dropdb --if-exists %s' % app_config.PROJECT_SLUG)
    local('createdb %s' % app_config.PROJECT_SLUG)

@task
def drop_tables():
    db = dataset.connect(app_config.POSTGRES_URL)

    for table in db.tables:
        print 'Dropping %s' % table
        table_obj = db[table]
        table_obj.drop()

@task
def fix_facebook_ids():
    """
    Retroactively adds Facebook IDs to Facebook table
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    table = db['facebook']

    min_created_time_result = list(db.query('select min(created_time) as min_created_time from facebook'))
    min_created_time = min_created_time_result[0]['min_created_time']

    graph = GraphAPI(SECRETS['FACEBOOK_TOKEN'])
    profile = graph.get_object(FACEBOOK_USER)
    posts = graph.get_connections(profile['id'], 'posts')

    done = False
    while not done:
        print 'processing batch of 25'
        for post in posts['data']:
            created_time = parser.parse(post['created_time'], ignoretz=True)
            if created_time < min_created_time:
                done = True
                break

            link = post['link'].split('?')[0]
            print 'updating %s (%s)' % (link, post['id'])
            table.update({
                'facebook_id': post['id'],
                'link_url': link,
            }, ['link_url'])

        posts = requests.get(posts['paging']['next']).json()
