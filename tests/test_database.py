import dataset
import unittest

from datetime import datetime
from fabric.api import local
from scrapers.facebook import FacebookScraper
from scrapers.homepage import HomepageScraper
from scrapers.seamus import SeamusScraper
from time import time

class TestDatabase(unittest.TestCase):
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
        seamus_scraper = SeamusScraper()
        seamus_stories = seamus_scraper.scrape_seamus(filename='tests/snapshots/query-current-04-21-2015.xml')
        seamus_scraper.write(self.db, seamus_stories)
        self.seamus_row = self.db['seamus'].find_one(id=6)

    def test_seamus_runtime(self):
        self.assertIsInstance(self.seamus_row['run_time'], datetime)

    def test_seamus_pub_date(self):
        self.assertEqual(self.seamus_row['publication_date'], datetime(2015, 4, 21, 11, 3, 0))

    def test_seamus_story_date(self):
        self.assertEqual(self.seamus_row['story_date'], datetime(2015, 4, 21, 11, 3, 15))

    def test_seamus_last_mod_date(self):
        self.assertEqual(self.seamus_row['last_modified_date'], datetime(2015, 4, 21, 11, 3, 15))

    def test_seamus_lead_art(self):
        self.assertIsInstance(self.seamus_row['has_lead_art'], bool)
        self.assertEqual(self.seamus_row['has_lead_art'], True)
