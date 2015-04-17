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
        self.first = self.articles[0]
        self.first_bullet = self.articles[2]

    def test_headline(self):
        self.assertEqual(self.first.headline, 'When The World Bank Does More Harm Than Good')
        self.assertEqual(self.first_bullet.headline, 'For Marathon Bombing Survivors, World Still Feels Out Of Control')

    def test_url(self):
        self.assertEqual(self.first.url, 'http://www.npr.org/blogs/goatsandsoda/2015/04/17/399816448/when-the-world-bank-does-more-harm-than-good')
        self.assertEqual(self.first_bullet.url, 'http://www.npr.org/blogs/health/2015/04/15/399616139/bombing-survivors-face-a-world-that-still-feels-out-of-control')

    def test_is_bullet(self):
        self.assertFalse(self.first.is_bullet)
        self.assertTrue(self.first_bullet.is_bullet)

    def test_story_id(self):
        self.assertEqual(self.first.story_id, '399816448')
        self.assertEqual(self.first_bullet.story_id, '399616139')

    def test_layout(self):
        self.assertEqual(self.articles[2].layout, 'bullet')
        self.assertEqual(self.articles[12].layout, 'video')
        self.assertEqual(self.articles[0].layout, 'big-image')
        self.assertEqual(self.articles[1].layout, 'small-image')
        self.assertEqual(self.articles[8].layout, None)

    def test_has_audio(self):
        self.assertTrue(self.articles[0].has_audio)
        self.assertFalse(self.articles[3].has_audio)

    def test_num_articles(self):
        self.assertEqual(len(self.articles), 22)
