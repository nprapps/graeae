#!/usr/bin/env python

"""
Cron jobs
"""
import app_config
import dataset

from fabric.api import local, require, task

from scrapers.facebook import FacebookScraper
from scrapers.homepage import HomepageScraper
from scrapers.seamus import SeamusScraper

@task
def test():
    """
    Example cron task. Note we use "local" instead of "run"
    because this will run on the server.
    """
    require('settings', provided_by=['production', 'staging'])

    local('echo $DEPLOYMENT_TARGET > /tmp/cron_test.txt')

@task
def scrape_homepage():
    """
    Run scrapers!
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    scraper = HomepageScraper()
    articles = scraper.scrape_homepage()
    api_entries = scraper.scrape_api_entries(articles)
    scraper.write(db, articles, api_entries)

@task
def scrape_facebook():
    db = dataset.connect(app_config.POSTGRES_URL)
    scraper = FacebookScraper()
    posts = scraper.scrape_facebook()
    insights = scraper.scrape_insights(posts)
    scraper.write(db, posts, insights)

@task
def scrape_seamus():
    db = dataset.connect(app_config.POSTGRES_URL)
    scraper = SeamusScraper()
    stories = scraper.scrape_seamus()
    scraper.write(db, stories)
