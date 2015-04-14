from pyquery import PyQuery

class Article:
    def __init__(self, element, slot):
        self.element = element
        self.slot = slot

    def serialize(self):
        return {
            'story_id': self.story_id,
            'slot': self.slot,
            'headline': self.headline,
            'url': self.url,
            'is_bullet': self.is_bullet,
            'has_image': self.has_image,
        }

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
    def has_image(self):
        return bool(self.element('figure').length)
