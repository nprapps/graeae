#!/usr/bin/env python

from datetime import datetime
import os
import requests

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
        print 'Scraping homepage'
        print '-----------------'

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

            if not element.attr('id'):
                continue

            if not element.hasClass('attachment'):
                slot += 1

            article = Article(element, slot, self.run_time)
            print article.headline

            articles.append(article)

        return articles

    def scrape_api_entries(self, articles):
        """
        Scrape NPR API for all articles.
        """
        print 'Scraping API         '
        print '------------'

        api_entries = []

        for article in articles:
            print article.story_id
            api_entries.append(self.scrape_api_entry(article))

        return api_entries

    def scrape_api_entry(self, article, **kwargs):
        """
        Scrape NPR API for a single article.
        """
        if not kwargs:
            response = requests.get('http://api.npr.org/query?id=%s&apiKey=%s' % (article.story_id, os.environ['NPR_API_KEY']))

            element = PyQuery(response.content)
        else:
            element = PyQuery(**kwargs)

        return ApiEntry(element)

    def write(self, db, articles, api_entries):
        """
        Write to database
        """
        table = db['homepage']

        for article, api_entry in zip(articles, api_entries):
            row = article.serialize()
            row.update(api_entry.serialize())
            table.insert(row)
