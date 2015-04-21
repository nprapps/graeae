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

    def test_story_date(self):
        self.assertEqual(self.stories[0].story_date, 'Tue, 21 Apr 2015 08:40:23 -0400')

    def test_publication_date(self):
        self.assertEqual(self.stories[0].publication_date, 'Tue, 21 Apr 2015 08:40:00 -0400')

    def test_last_modified_date(self):
        self.assertEqual(self.stories[0].last_modified_date, 'Tue, 21 Apr 2015 08:40:23 -0400')

    def test_canonical_url(self):
        self.assertEqual(self.stories[0].canonical_url, 'http://www.npr.org/blogs/thetwo-way/2015/04/21/401157787/top-stories-ex-egypt-leader-sentenced-blue-bell-recall-expands')
