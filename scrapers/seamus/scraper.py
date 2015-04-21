#!/usr/bin/env python

from datetime import datetime
import os
import requests

from pyquery import PyQuery

from app_config import get_secrets
from models import Story

SECRETS = get_secrets()

class SeamusScraper:
    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_seamus(self, **kwargs):
        """
        Scrape!
        """
        print 'Scraping Seamus'
        print '---------------'

        if not kwargs:
            response = requests.get('http://api.npr.org/query', params={
                'date': 'current',
                'orgId': '1',
                'apiKey': SECRETS['NPR_API_KEY']})

            element = PyQuery(response.content)
        else:
            element = PyQuery(**kwargs)

        story_elements = element.find('story')
        stories = []

        for story_el in story_elements:
            story_el = PyQuery(story_el)
            print story_el.attr('id')
            stories.append(Story(story_el, self.run_time))

        return stories

    def write(self, db, stories):
        """
        Write to database
        """
        table = db['seamus']

        for story in stories:
            exists = table.find_one(id=story.id)

            if exists:
                continue

            row = story.serialize()
            table.insert(row)
