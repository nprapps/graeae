#!/usr/bin/env python

from datetime import datetime
import logging
import os
import requests

from pyquery import PyQuery

from app_config import get_secrets
from models import Story

SECRETS = get_secrets()
SEAMUS_API_PAGE_SIZE = 20

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SeamusScraper:
    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_seamus(self, **kwargs):
        """
        Scrape!
        """
        logger.info('Scraping Seamus API (start time: %s)' % self.run_time)

        if not kwargs:
            stories = self._get_stories_from_api()
        else:
            element = PyQuery(parser='xml', **kwargs)
            story_elements = element.find('story')
            stories = self._extract_stories(story_elements)

        return stories

    def _get_stories_from_api(self):
        startNum = 1
        stories = []
        while True:
            response = requests.get('http://api.npr.org/query', params={
                'date': 'current',
                'orgId': '1',
                'apiKey': SECRETS['NPR_API_KEY'],
                'numResults': 20,
                'startNum': startNum,
            })

            element = PyQuery(response.content, parser='xml')
            story_elements = element.find('story')

            if len(story_elements):
                stories += self._extract_stories(story_elements)
                startNum += SEAMUS_API_PAGE_SIZE
            else:
                break

        return stories

    def _extract_stories(self, story_elements):
        stories = []

        for story_el in story_elements:
            story_el = PyQuery(story_el, parser='xml')
            story = Story(story_el, self.run_time)
            stories.append(story)
            logger.info('Scraped %s from Seamus API (%s)' % (story.story_id, story.title))

        return stories

    def write(self, db, stories):
        """
        Write to database
        """
        table = db['seamus']

        for story in stories:
            exists = table.find_one(story_id=story.story_id)

            if exists:
                continue

            row = story.serialize()
            table.insert(row)
