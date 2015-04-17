from pyquery import PyQuery

class Article:
    def __init__(self, element, slot, run_time):
        self.element = element
        self.slot = slot
        self.run_time = run_time

    def serialize(self):
        return {
            'layout': self.layout,
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
