from collections import OrderedDict
from itertools import groupby

import os
import urlparse

class Post:
    def __init__(self, api_post, run_time):
        self.api_post = api_post
        self.run_time = run_time

    def serialize(self):
        return OrderedDict([
            ('run_time', self.run_time),
            ('headline', self.headline),
            ('post_type', self.post_type),
            ('art_url', self.art_url),
            ('link_url', self.link_url),
        ])

    @property
    def id(self):
        return self.api_post['id']

    @property
    def headline(self):
        return self.api_post['name']

    @property
    def post_type(self):
        return self.api_post['type']

    @property
    def art_url(self):
        url = self.api_post['picture']
        params = urlparse.parse_qs(url[url.find('?'):])
        image_url = params['url'][0]
        return image_url[:image_url.find('?')]

    @property
    def link_url(self):
        url = self.api_post['link']
        return url[:url.find('?')]


class Insights:
    def __init__(self, post, api_insights):
        self.post = post
        self.api_insights = api_insights

    def serialize(self):
        return OrderedDict([
            ('shares', self.shares),
            ('likes', self.likes),
            ('comments', self.comments),
            ('people_reached', self.people_reached),
            ('photo_view_clicks', self.photo_view_clicks),
            ('link_clicks', self.link_clicks)
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

    def _post_consumptions_by_type(self, action_type):
        insight =  self._insights()['post_consumptions_by_type']
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

    @property
    def people_reached(self):
        return self._insights()['post_impressions_unique']['values'][0]['value']

    @property
    def photo_view_clicks(self):
        return self._post_consumptions_by_type('photo view')

    @property
    def link_clicks(self):
        return self._post_consumptions_by_type('link clicks')

    @property
    def other_clicks(self):
        """
        Numbers for this metric don't seem to match what is displayed on the
        post insights popup. Leaving out of reporting.
        """
        return self._post_consumptions_by_type('other clicks')
