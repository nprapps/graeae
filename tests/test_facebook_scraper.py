#!/usr/bin/env python

import unittest
import app_config

from scrapers.facebook import FacebookScraper

class TestScrapeFacebook(unittest.TestCase):
    def setUp(self):
        self.scraper = FacebookScraper()
        self.posts = self.scraper.scrape_facebook()

    def test_headline(self):
        self.assertEqual(self.posts[0].headline, 'NOPE NOPE NOPE')
