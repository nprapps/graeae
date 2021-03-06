from collections import OrderedDict
from scrapers.utils import get_art_root_url, get_seamus_id_from_url

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
            ('homepage_art_url', self.homepage_art_url),
            ('homepage_art_root_url', self.homepage_art_root_url),
            ('has_audio', self.has_audio),
            ('is_apps_project', self.is_apps_project),
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
        return get_seamus_id_from_url(self.url)

    @property
    def is_apps_project(self):
        url_parts = self.url.split('/')
        return url_parts[2].startswith('apps.')

    @property
    def teaser(self):
        if self.is_bullet:
            return None
        return self.element('.teaser').text()

    @property
    def layout(self):
        """
        Possible layouts: ['bullet', 'video', 'big-image', 'small-image', 'slideshow']
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

        if bucketwrap.hasClass('slideshow'):
            return 'slideshow'

        return None

    @property
    def homepage_art_url(self):
        if self.layout in ('big-image', 'small-image'):
            return self.element.find('.bucketwrap img').attr('data-original')

        return None

    @property
    def homepage_art_root_url(self):
        if self.homepage_art_url:
            return get_art_root_url(self.homepage_art_url)
        return None

    @property
    def has_audio(self):
        return bool(self.element.hasClass('post-type-audio'))

class ApiEntry:
    def __init__(self, article, element):
        self.article = article
        self.element = element

    def serialize(self):
        return OrderedDict([
            ('has_story_art', self.has_story_art),
            ('has_lead_art', self.has_lead_art),
            ('lead_art_provider', self.lead_art_provider),
            ('lead_art_url', self.lead_art_url),
            ('lead_art_root_url', self.lead_art_root_url),
            ('homepage_art_provider', self.homepage_art_provider),
        ])

    def _lead_art_element(self):
        art_elements = self.element.find('layout').find('storytext').children()

        if not len(art_elements):
            return None

        el = PyQuery(art_elements[0])

        if el[0].tag != 'image':
            return None

        image_id = el.attr('refId')

        return PyQuery(self.element.children('image[id="%s"]' % image_id))

    @property
    def has_story_art(self):
        return self.element.find('layout').find('image').length > 0

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

    @property
    def lead_art_root_url(self):
        if self.lead_art_url:
            return get_art_root_url(self.lead_art_url)
        return None

    def _parse_art_id_from_url(self, url):
        prefix = url[:url.rfind('_')]
        art_id = prefix.split('/')[-1]

        return art_id

    @property
    def homepage_art_provider(self):
        url = self.article.homepage_art_url

        if not url:
            return None

        art_id = self._parse_art_id_from_url(url)

        image_elements = self.element.children('image')

        # work around for https://github.com/nprapps/graeae/issues/82
        if not len(image_elements):
            return None

        for image_el in image_elements:
            src = PyQuery(image_el).attr('src')
            src_art_id = self._parse_art_id_from_url(src)

            if art_id == src_art_id:
                break

        return image_el.find('provider').text
