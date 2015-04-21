from collections import OrderedDict
from dateutil import parser
from itertools import groupby
from pytz import timezone

import os

class Story:
    """
    Represents a story in the Seamus API
    """
    def __init__(self, api_story, run_time):
        self.api_story = api_story
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('run_time', self.run_time),
            ('id', self.id),
            ('title', self.title),
            ('publication_date', self.publication_date),
            ('story_date', self.story_date),
            ('last_modified_date', self.last_modified_date),
            ('canonical_url', self.canonical_url),
        ])

    def _parse_date(self, date_string):
        parsed = parser.parse(date_string)
        adjusted = parsed.astimezone(timezone('UTC')).replace(tzinfo=None)
        return adjusted

    @property
    def id(self):
        """
        Get the story ID
        """
        return self.api_story.attr('id')

    @property
    def title(self):
        """
        Get the title
        """
        return self.api_story.children('title').text()

    @property
    def publication_date(self):
        """
        Get the publication date
        """
        return self._parse_date(self.api_story.children('pubDate').text())

    @property
    def story_date(self):
        """
        Get the story date
        """
        return self._parse_date(self.api_story.children('storyDate').text())

    @property
    def last_modified_date(self):
        """
        Get the last modified date
        """
        return self._parse_date(self.api_story.children('lastModifiedDate').text())

    @property
    def canonical_url(self):
        """
        Get the canonical URL
        """
        url = self.api_story.children('link[type="html"]').text()
        if url.find('?') > -1:
            return url[:url.find('?')]
        else:
            return url
