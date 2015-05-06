#!/usr/bin/env python

from datetime import datetime
import logging
import os
import requests

from pyquery import PyQuery

from app_config import get_secrets
from models import ApiEntry, Article

SECRETS = get_secrets()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class HomepageScraper:
    url = 'http://npr.org'

    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_homepage(self, **kwargs):
        """
        Scrape!
        """
        logger.info('Scraping homepage (start time: %s)' % self.run_time)

        if not kwargs:
            response = requests.get(self.url)

            page = PyQuery(response.content)
        else:
            page = PyQuery(**kwargs)

        article_elements = page('.stories-wrap article')
        slot = 0
        articles = []

        for el in article_elements:
            element = PyQuery(el)

            article = Article(element, self.run_time)

            if not article.is_story_link:
                continue

            if not element.hasClass('attachment'):
                slot += 1

            article.slot = slot
            articles.append(article)
            logger.info('Scraped %s from homepage (%s)' % (article.story_id, article.headline))

        return articles

    def scrape_api_entries(self, articles, **kwargs):
        """
        Scrape NPR API for all articles.
        """
        api_entries = []

        for article in articles:
            api_entries.append(self.scrape_api_entry(article, **kwargs))
            logger.info('Scraped %s from Seamus API (%s)' % (article.story_id, article.headline))

        return api_entries

    def scrape_api_entry(self, article, **kwargs):
        """
        Scrape NPR API for a single article.
        """
        if not kwargs:
            response = requests.get('http://api.npr.org/query', params={
                'id': article.story_id,
                'apiKey': SECRETS['NPR_API_KEY']})

            element = PyQuery(response.content, parser='xml').find('story')
        else:
            element = PyQuery(parser='xml', **kwargs).find('story')

        return ApiEntry(article, element)

    def write(self, db, articles, api_entries):
        """
        Write to database
        """
        table = db['homepage']

        for article, api_entry in zip(articles, api_entries):
            row = article.serialize()
            row.update(api_entry.serialize())
            table.insert(row)
