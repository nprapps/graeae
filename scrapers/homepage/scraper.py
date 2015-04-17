#!/usr/bin/env python

from datetime import datetime
from models import Article
from pyquery import PyQuery

class HomepageScraper:
    url = 'http://npr.org'

    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape(self, **kwargs):
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

    def write(self, articles, db):
        """
        Write to database
        """
        table = db['homepage']
        for article in articles:
            table.insert(article.serialize())
