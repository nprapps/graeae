#!/usr/bin/env python

import dataset
import unittest
import app_config

from scrapers.seamus import SeamusScraper

class TestScrapeSeamus(unittest.TestCase):
    def setUp(self):
        self.scraper = SeamusScraper()
        self.stories = self.scraper.scrape_seamus(filename='tests/snapshots/query-current-04-21-2015.xml')

    def test_id(self):
        self.assertEqual(self.stories[0].id, '401157787')

    def test_headline(self):
        self.assertEqual(self.stories[0].title, 'Top Stories: Ex-Egypt Leader Sentenced; Blue Bell Recall Expands')
