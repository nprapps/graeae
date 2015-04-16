from pyquery import PyQuery

class Article:
    def __init__(self, element, slot, runtime):
        self.element = element
        self.slot = slot
        self.runtime = runtime

    def serialize(self):
        return {
            'has_image': self.has_image,
            'headline': self.headline,
            'is_bullet': self.is_bullet,
            'run_time': self.run_time,
            'slot': self.slot,
            'story_id': self.story_id,
            'url': self.url,
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
