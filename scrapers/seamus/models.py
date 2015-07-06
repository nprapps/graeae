from collections import OrderedDict
from dateutil import parser
from itertools import groupby
from pytz import timezone
from pyquery import PyQuery
from scrapers.homepage.models import ApiEntry

import os
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Story(ApiEntry):
    """
    Represents a story in the Seamus API
    """
    def __init__(self, element, run_time):
        self.element = element
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('run_time', self.run_time),
            ('story_id', self.story_id),
            ('title', self.title),
            ('publication_date', self.publication_date),
            ('story_date', self.story_date),
            ('last_modified_date', self.last_modified_date),
            ('canonical_url', self.canonical_url),
            ('has_lead_art', self.has_lead_art),
            ('lead_art_provider', self.lead_art_provider),
            ('lead_art_url', self.lead_art_url),
            ('lead_art_root_url', self.lead_art_root_url),
            ('has_audio', self.has_audio),
            ('slug', self.slug),
        ])

    def _parse_date(self, date_string):
        parsed = parser.parse(date_string)
        try:
            adjusted = parsed.astimezone(timezone('UTC')).replace(tzinfo=None)
            return adjusted
        except ValueError:
            logger.warning('Datetime for %s was naive' % self.story_id)
            return parsed

    @property
    def story_id(self):
        """
        Get the story ID
        """
        return self.element.attr('id')

    @property
    def title(self):
        """
        Get the title
        """
        return self.element.children('title').text()

    @property
    def publication_date(self):
        """
        Get the publication date
        """
        return self._parse_date(self.element.children('pubDate').text())

    @property
    def story_date(self):
        """
        Get the story date
        """
        return self._parse_date(self.element.children('storyDate').text())

    @property
    def last_modified_date(self):
        """
        Get the last modified date
        """
        return self._parse_date(self.element.children('lastModifiedDate').text())

    @property
    def canonical_url(self):
        """
        Get the canonical URL
        """
        url = self.element.children('link[type="html"]').text()
        if url.find('?') > -1:
            return url[:url.find('?')]
        else:
            return url

    @property
    def has_audio(self):
        """
        Get if the story has audio
        """
        return bool(self.element.children('audio'))

    @property
    def slug(self):
        """
        Get the slug/vertical of a story
        """
        return self.element.children('slug').text()
