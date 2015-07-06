#!/usr/bin/env python

import app_config
import dataset
import datetime
import logging
import static

from flask import Flask, make_response, render_template, jsonify
from scrapers.utils import get_art_root_url
from sqlalchemy.exc import ProgrammingError
from render_utils import make_context, smarty_filter, urlencode_filter
from render_utils import format_commas_filter
from werkzeug.debug import DebuggedApplication
from urllib import unquote

SITE_USERS = [
    {'name': 'Ariel Zambelich'},
    {'name': 'David Gilkey'},
    {'name': 'Emily Bogle'},
    {'name': 'Kainaz Amaria'},
    {'name': 'Lydia Thompson'},
]

app = Flask(__name__)
app.debug = app_config.DEBUG

try:
    file_handler = logging.FileHandler('%s/public_app.log' % app_config.SERVER_LOG_PATH)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
except IOError:
    pass

app.logger.setLevel(logging.INFO)

app.register_blueprint(static.static, url_prefix='/%s' % app_config.PROJECT_SLUG)

app.add_template_filter(smarty_filter, name='smarty')
app.add_template_filter(urlencode_filter, name='urlencode')
app.add_template_filter(format_commas_filter, name='format_commas')

# Example of rendering index.html with public_app 
@app.route('/%s/' % app_config.PROJECT_SLUG, methods=['GET'])
def index():
    """
    Example view rendering a simple page.
    """
    context = make_context(asset_depth=1)

    context['users'] = SITE_USERS

    return make_response(render_template('admin/index.html', **context))

@app.route('/%s/get-image/' % app_config.PROJECT_SLUG, methods=['GET'])
@app.route('/%s/get-image/<offset>' % app_config.PROJECT_SLUG, methods=['GET'])
def get_image(offset=0):
    from flask import request

    db = dataset.connect(app_config.POSTGRES_URL)

    evaluator = unquote(request.cookies['graeae_user'])

    try:
        result = db.query("""
            select s.lead_art_url
            from seamus s
            left join
                (select image_url from evaluated_images where evaluator = '{0}') ev
                on s.lead_art_url = ev.image_url
            where ev.image_url is Null and s.lead_art_url is not Null
            limit 1
            offset {1}
        """.format(evaluator, offset))
    except ProgrammingError:
        table = db['seamus']
        result = table.find(has_lead_art=True, _limit=1, _offset=int(offset))

    image_list = list(result)

    if len(image_list):
        image = image_list.pop()
        root, ext = image['lead_art_url'].rsplit('.', 1)
        data = {
            'thumb_url': '{0}-s800.{1}'.format(root, ext),
            'image_url': image['lead_art_url'],
        }
    else:
        data = {}

    return jsonify(**data)


@app.route('/%s/save-image/' % app_config.PROJECT_SLUG, methods=['POST'])
def save_image():
    from flask import request

    db = dataset.connect(app_config.POSTGRES_URL)
    table = db['evaluated_images']

    data = {
        'evaluator': request.form['evaluator'],
        'image_url': request.form['image_url'],
        'image_root_url': get_art_root_url(request.form['image_url']),
    }

    if request.form['quality'] == 'love':
        data['is_good'] = True
    else:
        data['is_good'] = False

    table.upsert(data, ['evaluator', 'image_url'])

    return 'success'

@app.route('/%s/leaderboard/' % app_config.PROJECT_SLUG, methods=['GET'])
def leaderboard():
    """
    leaderboard for photo evaluations
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    context = make_context(asset_depth=1)

    context['total_images'] = _total_query(db)
    context['leaderboard'] = _leaderboard_query(db)
    context['top_loved'] = _top_loved_query(db)
    context['top_hated'] = _top_hated_query(db)

    return make_response(render_template('admin/leaderboard.html', **context))

def _leaderboard_query(db):
    """
    Query for leaderboard
    """
    result = db.query("""
        select evaluator,
               sum(case when is_good then 1 else 0 end) as fleek,
               sum(case when is_good is false then 1 else 0 end) as shade,
               count(is_good) as total,
               sum(case when is_good then 1.0 else 0 end) / count(is_good) * 100 as fleek_pct,
               sum(case when is_good is false then 1.0 else 0 end) / count(is_good) * 100 as shade_pct
        from evaluated_images
        group by evaluator
        order by total desc
    """)
    result_list = list(result)

    grand_total_result = db.query("""
        select
               sum(case when is_good then 1 else 0 end) as fleek,
               sum(case when is_good is false then 1 else 0 end) as shade,
               count(is_good) as total,
               sum(case when is_good then 1.0 else 0 end) / count(is_good) * 100 as fleek_pct,
               sum(case when is_good is false then 1.0 else 0 end) / count(is_good) * 100 as shade_pct
        from evaluated_images
    """)

    grand_total_row = list(grand_total_result).pop()
    grand_total_row['evaluator'] = 'Total'

    result_list.append(grand_total_row)

    return result_list

def _total_query(db):
    """
    Query # of lead art elements
    """
    result = db.query("""
        select count(distinct(lead_art_url)) as count
        from seamus
    """)
    value = list(result).pop()
    return value['count']

def _top_loved_query(db):
    result = db.query("""
        select ev.image_url, s.title, s.canonical_url,
               sum(case when is_good then 1 else 0 end) as fleek
        from evaluated_images ev
        join seamus s on s.lead_art_url = ev.image_url
        where {0}
        group by ev.image_url, s.title, s.canonical_url
        order by fleek desc
        limit 10
    """.format(_editors()))
    result_list = list(result)
    for row in result_list:
        row['image_url'] = _get_small_image(row['image_url'])
    return result_list

def _top_hated_query(db):
    result = db.query("""
        select ev.image_url, s.title, s.canonical_url,
               sum(case when is_good is false then 1 else 0 end) as shade
        from evaluated_images ev
        join seamus s on s.lead_art_url = ev.image_url
        where {0}
        group by ev.image_url, s.title, s.canonical_url
        order by shade desc
        limit 10
    """.format(_editors()))
    result_list = list(result)
    for row in result_list:
        row['image_url'] = _get_small_image(row['image_url'])
    return result_list

def _get_small_image(url):
    root, ext = url.rsplit('.', 1)
    return '{0}-s200.{1}'.format(root, ext)

def _editors():
    quoted_list = ["'{0}'".format(user['name']) for user in SITE_USERS]
    query_fragment = "evaluator in ({0})".format(", ".join(quoted_list))
    return query_fragment

# Enable Werkzeug debug pages
if app_config.DEBUG:
    wsgi_app = DebuggedApplication(app, evalex=False)
else:
    wsgi_app = app

# Catch attempts to run the app directly
if __name__ == '__main__':
    print 'This command has been removed! Please run "fab public_app" instead!'
