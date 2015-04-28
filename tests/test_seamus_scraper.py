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

    def test_has_lead_art(self):
        self.assertEqual(self.stories[0].has_lead_art, False)
        self.assertEqual(self.stories[6].has_lead_art, True)

    def test_lead_art_provider(self):
        print self.stories[6].canonical_url
        self.assertEqual(self.stories[6].lead_art_provider, 'Mohamed El-Shahed/AFP/Getty Images')

    def test_lead_art_url(self):
        print self.stories[6].lead_art_url
        self.assertEqual(self.stories[6].lead_art_url, 'http://media.npr.org/assets/img/2015/04/21/morsi-court_wide-27506a416e57aafb2da92954aa1b28a88df7d467.jpg')

