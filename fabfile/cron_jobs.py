#!/usr/bin/env python

"""
Cron jobs
"""
import app_config
import dataset
import flat
import time

from fabric.api import local, require, task

from oauth import get_document
from scrapers.facebook import FacebookScraper
from scrapers.homepage import HomepageScraper
from scrapers.seamus import SeamusScraper
from scrapers.spreadsheet import SpreadsheetScraper
from scrapers.google_analytics import GoogleAnalyticsScraper

@task
def test():
    """
    Example cron task. Note we use "local" instead of "run"
    because this will run on the server.
    """
    require('settings', provided_by=['production', 'staging'])

    local('echo $DEPLOYMENT_TARGET > /tmp/cron_test.txt')

@task
def scrape():
    """
    Scrape everything
    """
    scrape_homepage()
    scrape_facebook()
    scrape_seamus()
    scrape_spreadsheet()

@task
def scrape_homepage():
    """
    Scrape homepage
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    scraper = HomepageScraper()
    articles = scraper.scrape_homepage()
    api_entries = scraper.scrape_api_entries(articles)
    scraper.write(db, articles, api_entries)

@task
def scrape_facebook():
    """
    Scrape Facebook
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    scraper = FacebookScraper()
    posts = scraper.scrape_facebook()
    insights = scraper.scrape_insights(posts)
    scraper.write(db, posts, insights)

@task
def scrape_seamus():
    """
    Scrape Seamus API
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    scraper = SeamusScraper()
    stories = scraper.scrape_seamus()
    scraper.write(db, stories)


@task
def scrape_spreadsheet():
    """
    Scrape 'Did we touch it?' spreadsheet
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    get_document(app_config.STORIES_GOOGLE_DOC_KEY, app_config.STORIES_PATH)
    scraper = SpreadsheetScraper()
    stories = scraper.scrape_spreadsheet(app_config.STORIES_PATH)
    scraper.write(db, stories)

@task
def scrape_google_analytics():
    db = dataset.connect(app_config.POSTGRES_URL)
    min_result = list(db.query("""
        select min(publication_date) as date
        from seamus
    """)).pop(0)

    scraper = GoogleAnalyticsScraper()
    rows = scraper.scrape_google_analytics(min_result['date'])
    scraper.write(db, rows)

@task
def backup():
    """
    Back up the database
    """
    import data
    today = time.strftime('%Y-%m-%d') 
    dst_directory = 'backup/{0}'.format(today)
    dump_directory = '/tmp/graeae-backup/{0}'.format(today)
    data.dump_db(dump_directory)
    flat.deploy_folder(app_config.BACKUP_S3_BUCKET, dump_directory, dst_directory)
    local('rm -Rf /tmp/graeae-backup')

