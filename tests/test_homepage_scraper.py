#!/usr/bin/env python

import dataset
import unittest
import app_config

from fabric.api import local
from nose.tools import assert_equal
from scrapers.homepage import HomepageScraper
from time import time

class TestScrapeHomepage(unittest.TestCase):
    def setUp(self):
        self.scraper = HomepageScraper()
        self.articles = self.scraper.scrape_homepage(filename='tests/snapshots/index-04-24-2015.html')
        self.first = self.articles[0]
        self.first_bullet = self.articles[1]

    def test_headline(self):
        self.assertEqual(self.first.headline, 'Remembering Gallipoli, A WWI Battle That Shaped Today\'s Middle East')
        self.assertEqual(self.first_bullet.headline, 'Turks And Armenians Prepare For Dueling Anniversaries')

    def test_url(self):
        self.assertEqual(self.first.url, 'http://www.npr.org/blogs/parallels/2015/04/24/401963898/remembering-gallipoli-a-wwi-battle-that-shaped-todays-middle-east')
        self.assertEqual(self.first_bullet.url, 'http://www.npr.org/blogs/parallels/2015/04/22/401508242/turks-and-armenians-prepare-for-dueling-anniversaries-on-friday')

    def test_is_bullet(self):
        self.assertFalse(self.first.is_bullet)
        self.assertTrue(self.first_bullet.is_bullet)

    def test_story_id(self):
        self.assertEqual(self.first.story_id, '401963898')
        self.assertEqual(self.first_bullet.story_id, '401508242')

    def test_layout(self):
        self.assertEqual(self.articles[0].layout, 'big-image')
        self.assertEqual(self.articles[1].layout, 'bullet')
        self.assertEqual(self.articles[2].layout, 'small-image')
        self.assertEqual(self.articles[4].layout, 'video')
        self.assertEqual(self.articles[9].layout, 'slideshow')
        self.assertEqual(self.articles[11].layout, None)

    def test_is_apps_project(self):
        self.assertEqual(self.articles[0].is_apps_project, False)
        self.assertEqual(self.articles[22].is_apps_project, True)

    def test_has_audio(self):
        self.assertTrue(self.articles[14].has_audio)
        self.assertFalse(self.articles[0].has_audio)

    def test_num_articles(self):
        self.assertEqual(len(self.articles), 29)

    def test_homepage_art_url(self):
        self.assertEqual(self.articles[0].homepage_art_url, 'http://media.npr.org/assets/img/2015/04/24/gallipoli-getty-01_wide-906fbf6d89a2544d138bbd29b4cb317a0e015dda-s900.jpg')
        self.assertIs(self.articles[11].homepage_art_url, None)

    def test_homepage_root_art_url(self):
        self.assertEqual(self.articles[0].homepage_root_art_url, 'http://media.npr.org/assets/img/2015/04/24/gallipoli-getty-01.jpg')
        self.assertIs(self.articles[11].homepage_root_art_url, None)

    def test_teaser(self):
        self.assertEqual(self.articles[0].teaser, 'The Gallipoli campaign saw Ottoman forces, fighting under German command, repel an allied attack led by Britain and France. Its reverberations are still felt to this day in the chaotic Middle East.')

class TestScrapeApi(unittest.TestCase):
    def setUp(self):
        self.scraper = HomepageScraper()
        self.articles = self.scraper.scrape_homepage(filename='tests/snapshots/index-04-17-2015-1000.html')
        self.api_entry = self.scraper.scrape_api_entry(self.articles[0], filename='tests/snapshots/query-399816448-04-17-2015.xml')

    def test_has_story_art(self):
        self.assertTrue(self.api_entry.has_story_art)

    def test_has_lead_art(self):
        self.assertTrue(self.api_entry.has_lead_art)

    def test_lead_art_provider(self):
        self.assertEqual(self.api_entry.lead_art_provider, 'AFP/Getty Images')

    def test_lead_art_url(self):
        self.assertEqual(self.api_entry.lead_art_url, 'http://media.npr.org/assets/img/2015/04/15/463942430-a6ceb5d9f82976adf38dfa46c6eb125b7af2ce62.jpg')

    def test_lead_root_art_url(self):
        self.assertEqual(self.api_entry.lead_root_art_url, 'http://media.npr.org/assets/img/2015/04/15/463942430-a6ceb5d9f82976adf38dfa46c6eb125b7af2ce62.jpg')

    def test_homepage_art_provider(self):
        self.assertEqual(self.api_entry.homepage_art_provider, 'AFP/Getty Images')
