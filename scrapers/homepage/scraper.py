#!/usr/bin/env python

from datetime import datetime
import os

from pyquery import PyQuery

from models import ApiEntry, Article

class HomepageScraper:
    url = 'http://npr.org'

    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_homepage(self, **kwargs):
        """
        Scrape!
        """
        if not kwargs:
            page = PyQuery(url=self.url)
        else:
            page = PyQuery(**kwargs)

        article_elements = page('.stories-wrap article')
        slot = 0
        articles = []
        for el in article_elements:
            element = PyQuery(el)
            if not element.hasClass('attachment'):
                slot += 1
            articles.append(Article(element, slot, self.run_time))

        return articles

    def scrape_api_entries(self, articles):
        """
        Scrape NPR API for all articles.
        """
        api_entries = []

        for article in articles:
            api_entries.append(scrape_api_entry(article))

        return api_entries

    def scrape_api_entry(self, article, **kwargs):
        """
        Scrape NPR API for a single article.
        """
        if not kwargs:
            element = PyQuery(url='http://api.npr.org/query?id=%s&apiKey=%s' % (article.story_id, os.environ['NPR_API_KEY']))
        else:
            element = PyQuery(**kwargs)

        return ApiEntry(element)

    def write(self, articles, db):
        """
        Write to database
        """
        table = db['homepage']
        for article in articles:
            table.insert(article.serialize())
