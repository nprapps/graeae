from collections import OrderedDict
import os

from pyquery import PyQuery

class Article:
    def __init__(self, element, run_time):
        self.element = element
        self.slot = None
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('layout', self.layout),
            ('headline', self.headline),
            ('is_bullet', self.is_bullet),
            ('run_time', self.run_time),
            ('slot', self.slot),
            ('story_id', self.story_id),
            ('url', self.url),
            ('homepage_image', self.homepage_image),
        ])

    @property
    def headline(self):
        return self.element('h1.title').text()

    @property
    def url(self):
        return self.element('h1.title').parents('a').attr('href')

    @property
    def is_bullet(self):
        return self.element.hasClass('attachment')

    @property
    def story_id(self):
        url_parts = self.url.split('/')
        return url_parts[-2]

    @property
    def is_story_link(self):
        return self.story_id.isdigit()

    @property
    def layout(self):
        """
        Possible layouts: ['bullet', 'video', 'big-image', 'small-image']
        """
        if self.is_bullet:
            return 'bullet'

        bucketwrap = self.element.find('.bucketwrap')

        if bucketwrap.hasClass('video'):
            return 'video'

        if bucketwrap.hasClass('homeLarge'):
            return 'big-image'

        if bucketwrap.hasClass('homeThumb'):
            return 'small-image'

        return None

    @property
    def has_audio(self):
        return bool(self.element.hasClass('post-type-audio'))

class ApiEntry:
    def __init__(self, element):
        self.element = element

    def serialize(self):
        return OrderedDict([
            ('has_story_image', self.has_story_image),
            ('has_lead_art', self.has_lead_art),
            ('lead_art_provider', self.lead_art_provider),
            ('lead_art_url', self.lead_art_url)
        ])

    @property
    def has_story_image(self):
        return self.element.find('layout').find('image').length > 0

    def _lead_art_element(self):
        el = PyQuery(self.element.find('layout').find('storytext').children()[0])

        if el[0].tag != 'image':
            return None

        image_id = el.attr('refId')

        return PyQuery(self.element.find('image[id="%s"]' % image_id))

    @property
    def has_lead_art(self):
        return bool(self._lead_art_element())

    @property
    def lead_art_provider(self):
        el = self._lead_art_element()

        if not el:
            return None

        return el.find('provider').text()

    @property
    def lead_art_url(self):
        el = self._lead_art_element()

        if not el:
            return None

        return PyQuery(el.find('enlargement')).attr('src')
