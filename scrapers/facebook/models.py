from collections import OrderedDict
import os

class Post:
    def __init__(self, api_post, run_time):
        self.api_post = api_post
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('headline', self.headline)
        ])

    @property
    def headline(self):
        return self.api_post['name']
