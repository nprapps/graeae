from collections import OrderedDict
from dateutil import parser
from itertools import groupby

import os
import urlparse


class Post:
    """
    Represent a Facebook post pulled from the Graph API
    """

    def __init__(self, api_post, run_time):
        self.api_post = api_post
        self.run_time = run_time

    def serialize(self):
        """
        Serialize post data
        """
        return OrderedDict([
            ('run_time', self.run_time),
            ('headline', self.headline),
            ('post_type', self.post_type),
            ('art_url', self.art_url),
            ('link_url', self.link_url),
            ('created_time', self.created_time),
            ('updated_time', self.updated_time),
            ('message', self.message),
            ('description', self.description),
        ])

    @property
    def id(self):
        """
        Get post ID
        """
        return self.api_post['id']

    @property
    def headline(self):
        """
        Get headline (headlines are optional)
        """
        return self.api_post.get('name')

    @property
    def post_type(self):
        """
        Get post type (e.g. 'link')
        """
        return self.api_post['type']

    @property
    def created_time(self):
        """
        Get created time
        """
        return parser.parse(self.api_post['created_time'], ignoretz=True)

    @property
    def updated_time(self):
        """
        Get updated time
        """
        return parser.parse(self.api_post['updated_time'], ignoretz=True)

    @property
    def art_url(self):
        """
        Get url to featured image
        """
        try:
            url = self.api_post['picture']
        except KeyError:
            return None

        # If there's a URL parameter, use it, otherwise the image was directly
        # uploaded to FB
        try:
            params = urlparse.parse_qs(url[url.find('?'):])
            image_url = params['url'][0]
            if image_url.find('?') > -1:
                image_url = image_url[:image_url.find('?')]
        except KeyError:
            image_url = url

        return image_url

    @property
    def link_url(self):
        """
        Get post link url
        """
        url = self.api_post['link']
        if url.find('?') > -1:
            return url[:url.find('?')]
        else:
            return url

    @property
    def message(self):
        """
        Get message (the text above the photo)
        """
        return self.api_post.get('message')

    @property
    def description(self):
        """
        Get description (the text associated with the photo)
        """
        return self.api_post.get('description')


class Insights:
    """
    Represent insights data for a Facebook post from the Graph API
    """

    def __init__(self, post, api_insights):
        self.post = post
        self.api_insights = api_insights

    def serialize(self):
        """
        Serialize insights data
        """
        try:
            return OrderedDict([
                ('shares', self.shares),
                ('likes', self.likes),
                ('comments', self.comments),
                ('people_reached', self.people_reached),
                ('photo_view_clicks', self.photo_view_clicks),
                ('link_clicks', self.link_clicks)
            ])
        except KeyError:
            return OrderedDict([
                ('shares', None),
                ('likes', None),
                ('comments', None),
                ('people_reached', None),
                ('photo_view_clicks', None),
                ('link_clicks', None)
            ])

    def _insights(self):
        """
        Coerce insights data into dict
        """
        insights = {}

        for row in self.api_insights['data']:
            insights[row['name']] = row

        return insights

    def _post_stories_by_action_type(self, action_type):
        """
        Parse 'post_stories_by_action_type'
        """
        insight =  self._insights()['post_stories_by_action_type']
        value = insight['values'][0]['value']

        if not value:
            return 0

        if action_type not in value:
            return 0

        return value[action_type]

    def _post_consumptions_by_type(self, action_type):
        """
        Parse 'post_consumptions_by_type'
        """
        insight =  self._insights()['post_consumptions_by_type']
        value = insight['values'][0]['value']

        if not value:
            return 0

        if action_type not in value:
            return 0

        return value[action_type]

    @property
    def shares(self):
        """
        Get shares value
        """
        return self._post_stories_by_action_type('share')

    @property
    def likes(self):
        """
        Get likes value
        """
        return self._post_stories_by_action_type('like')

    @property
    def comments(self):
        """
        Get comments value
        """
        return self._post_stories_by_action_type('comment')

    @property
    def people_reached(self):
        """
        Get people reached value
        """
        return self._insights()['post_impressions_unique']['values'][0]['value']

    @property
    def photo_view_clicks(self):
        """
        Get photo view value
        """
        return self._post_consumptions_by_type('photo view')

    @property
    def link_clicks(self):
        """
        Get link clicks value
        """
        return self._post_consumptions_by_type('link clicks')

    @property
    def other_clicks(self):
        """
        Get other clicks value

        Numbers for this metric don't seem to match what is displayed on the
        post insights popup. Leaving out of reporting.
        """
        return self._post_consumptions_by_type('other clicks')
