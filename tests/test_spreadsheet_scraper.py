#!/usr/bin/env python

import dataset
import unittest
import app_config

from datetime import datetime
from scrapers.spreadsheet import SpreadsheetScraper

class TestScrapeSpreadsheet(unittest.TestCase):
    def setUp(self):
        self.scraper = SpreadsheetScraper()
        self.stories = self.scraper.scrape_spreadsheet(filename='tests/snapshots/did-visuals-touch-it.xlsx')

    def test_seamus_id(self):
        self.assertEqual(self.stories[1].seamus_id, '403291009')

    def test_duration(self):
        # This one is a none that should be zero
        self.assertEqual(self.stories[0].duration, 0)

        # Correct entry
        self.assertEqual(self.stories[1].duration, 0.5)

        # The next one was entered as a negative #
        self.assertEqual(self.stories[14].duration, 1)

    def test_contribution(self):
        self.assertEqual(self.stories[1].contribution, 'Request / tone / edit reporter or producer images, Source pre-existing images (photo or illustration) from the wires / Flickr / other newspapers / archives')

    def test_contributors(self):
        self.assertEqual(self.stories[0].contributors, 'Kainaz Amaria')
        self.assertEqual(self.stories[10].contributors, 'Ariel Zambelich, Emily Bogle, Ryan Kellman')

    def test_timestamp(self):
        self.assertEqual(self.stories[0].timestamp, datetime(2015, 4, 29, 14, 38, 32))
