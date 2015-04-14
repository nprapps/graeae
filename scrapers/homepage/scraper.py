#!/usr/bin/env python

import dataset

from models import Article
from pyquery import PyQuery
from pprint import pprint as pp

class HomepageScraper:
    url = 'http://npr.org'

    def __init__(self):
        self.page = PyQuery(url=self.url)

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
            article = Article(element, slot)
            pp(article.serialize())

if __name__ == '__main__':
    scraper = HomepageScraper()
    scraper.scrape()
