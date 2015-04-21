#!/usr/bin/env python

import dataset
import unittest
import app_config

from datetime import datetime
from scrapers.seamus import SeamusScraper

class TestScrapeSeamus(unittest.TestCase):
    def setUp(self):
        self.scraper = SeamusScraper()
        self.stories = self.scraper.scrape_seamus(filename='tests/snapshots/query-current-04-21-2015.xml')

    def test_id(self):
        self.assertEqual(self.stories[0].id, '401157787')

    def test_headline(self):
        self.assertEqual(self.stories[0].title, 'Top Stories: Ex-Egypt Leader Sentenced; Blue Bell Recall Expands')

    def test_story_date(self):
        self.assertEqual(self.stories[0].story_date, datetime(2015, 4, 21, 12, 40, 23))

    def test_publication_date(self):
        self.assertEqual(self.stories[0].publication_date, datetime(2015, 4, 21, 12, 40, 0))

    def test_last_modified_date(self):
        self.assertEqual(self.stories[0].last_modified_date, datetime(2015, 4, 21, 12, 40, 23))

    def test_canonical_url(self):
        self.assertEqual(self.stories[0].canonical_url, 'http://www.npr.org/blogs/thetwo-way/2015/04/21/401157787/top-stories-ex-egypt-leader-sentenced-blue-bell-recall-expands')
