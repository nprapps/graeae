from collections import OrderedDict
from itertools import groupby

import os


class Post:
    def __init__(self, api_post, insights, run_time):
        self.api_post = api_post
        self.insights_data = insights['data']
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('headline', self.headline),
            ('insights', self.insights),
        ])

    @property
    def headline(self):
        return self.api_post['name']

    @property
    def insights(self):
        insights = {}
        for row in self.insights_data['data']:
            insights[row['name']] = row

        return insights
