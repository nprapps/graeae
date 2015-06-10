#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
import app_config
import dataset
import ipdb
import logging
import requests

from dateutil import parser
from fabric.api import local, task
from facebook import GraphAPI
from scrapers.utils import get_art_root_url

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

    for table_name in db.tables:
        print 'Dropping %s' % table_name
        table = db[table_name]
        table.drop()

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

            if 'link' not in post.keys():
                print 'skipping %s (no link)' % post['id']
                continue

            link = post['link'].split('?')[0]
            print 'updating %s (%s)' % (link, post['id'])
            table.update({
                'facebook_id': post['id'],
                'link_url': link,
            }, ['link_url'])

        posts = requests.get(posts['paging']['next']).json()

@task
def fix_fb_art_urls():
    db = dataset.connect(app_config.POSTGRES_URL)

    fb = db['facebook']
    for row in fb.all():
        if row['art_url']:
            update = {
                'art_root_url': get_art_root_url(row['art_url']),
                'id': row['id']
            }
            print 'updating %s' % update
            fb.update(update, ['id'])


@task
def fix_homepage_art_urls():
    db = dataset.connect(app_config.POSTGRES_URL)
    hp = db['homepage']
    for row in hp.all():
        if row['homepage_art_url']:
            update = {
                'homepage_art_root_url': get_art_root_url(row['homepage_art_url']),
                'id': row['id']
            }
            print 'updating %s' % update
            hp.update(update, ['id'])


@task
def fix_seamus_art_urls():
    db = dataset.connect(app_config.POSTGRES_URL)
    seamus = db['seamus']
    for row in seamus.all():
        if row['lead_art_url']:
            update = {
                'lead_art_root_url': get_art_root_url(row['lead_art_url']),
                'id': row['id']
            }
            print 'updating %s' % update
            seamus.update(update, ['id']) 


@task
def db_shell():
    db = dataset.connect(app_config.POSTGRES_URL)
    print 'Dropping to interactive shell. The `db` variable has access to the current live database.'
    ipdb.set_trace()
    pass

@task
def dump_db(directory):
    """
    Dump the database. Directory required.
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    local('mkdir -p {0}'.format(directory))
    for table_name in db.tables:
        table = db[table_name]
        results = table.all()
        backup_filename = '{0}/{1}.csv'.format(directory, table_name)
        with open(backup_filename, 'w') as f:
            dataset.freeze(results, format='csv', fileobj=f)
