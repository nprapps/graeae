#!/usr/bin/env python

import app_config

from datetime import datetime
from models import Article
from pyquery import PyQuery
from pprint import pprint as pp

class HomepageScraper:
    url = 'http://npr.org'

    def __init__(self):
        self.run_time = datetime.utcnow()
        self.page = PyQuery(url=self.url)
        self.table = app_config.db['homepage']

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
            self.table.insert(article.serialize())
