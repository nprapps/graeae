#!/usr/bin/env python

import dataset
import unittest
import app_config

from fabric.api import local
from nose.tools import assert_equal
from scrapers.homepage import HomepageScraper
from time import time


class TestScraperDB(unittest.TestCase):
    """
    Test the scraper
    """
    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""
        klass.temp_db_name = 'graeae_%s' % int(time())
        local('createdb %s' % klass.temp_db_name)

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""
        local('dropdb %s' % klass.temp_db_name)

    def setUp(self):
        self.db = dataset.connect('postgres:///%s' % self.temp_db_name)
        self.scraper = HomepageScraper()

    def test_db_write(self):
        articles = self.scraper.scrape()
        self.scraper.write(articles, self.db)
        rows = list(self.db['homepage'].all())
        self.assertGreater(len(rows), 0)


class TestScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = HomepageScraper()
        self.articles = self.scraper.scrape(filename='tests/snapshots/index-04-17-2015-1000.html')

    def test_headline(self):
        first = self.articles[0]
        self.assertEqual(first.headline, 'When The World Bank Does More Harm Than Good')

    def test_num_articles(self):
        self.assertEqual(len(self.articles), 22)



