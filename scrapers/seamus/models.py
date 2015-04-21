from collections import OrderedDict
from itertools import groupby

import os

class Story:
    def __init__(self, api_story, run_time):
        self.api_story = api_story
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('run_time', self.run_time),
            ('id', self.id),
            ('title', self.title)
        ])

    @property
    def id(self):
        return self.api_story.attr('id')

    @property
    def title(self):
        return self.api_story.children('title').text()
