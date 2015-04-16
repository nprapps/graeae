#!/usr/bin/env python

import dataset

from datetime import datetime
from models import Article
from pyquery import PyQuery
from pprint import pprint as pp

class HomepageScraper:
    url = 'http://npr.org'

    def __init__(self):
        self.run_time = datetime.utcnow()
        self.page = PyQuery(url=self.url)
        self.db = dataset.connect(app_config.POSTGRES_URL)
        self.table = self.db['homepage']

    def scrape(self):
        """
        Scrape!
        """
        article_elements = self.page('.stories-wrap article')
        slot = 0
        for el in article_elements:
            element = PyQuery(el)
            if not element.hasClass('attachment'):
                slot += 1
            article = Article(element, slot, self.run_time)
            table.insert(article.serialize())

if __name__ == '__main__':
    if __package__ is None:
        __package__ = 'scrapers.homepage'
    scraper = HomepageScraper()
    scraper.scrape()
