from collections import OrderedDict
from itertools import groupby

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
    def id(self):
        return self.api_post['id']

    @property
    def headline(self):
        return self.api_post['name']

class Insights:
    def __init__(self, post, api_insights):
        self.post = post
        self.api_insights = api_insights

    def serialize(self):
        return OrderedDict([
            ('shares', self.shares),
            ('likes', self.likes),
            ('comments', self.comments)
        ])

    def _insights(self):
        insights = {}

        for row in self.api_insights['data']:
            insights[row['name']] = row

        return insights

    def _post_stories_by_action_type(self, action_type):
        insight =  self._insights()['post_stories_by_action_type']
        value = insight['values'][0]['value']

        if not value:
            return 0

        if action_type not in value:
            return 0

        return value[action_type]

    @property
    def shares(self):
        return self._post_stories_by_action_type('share')

    @property
    def likes(self):
        return self._post_stories_by_action_type('like')

    @property
    def comments(self):
        return self._post_stories_by_action_type('comment')
