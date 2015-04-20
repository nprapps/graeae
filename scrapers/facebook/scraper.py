#!/usr/bin/env python

from datetime import datetime

from facebook import GraphAPI

from app_config import get_secrets
from models import Post

SECRETS = get_secrets()

class FacebookScraper:
    access_token = SECRETS['FACEBOOK_TOKEN']
    user = 'NPR'

    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_facebook(self, **kwargs):
        """
        Scrape!
        """
        graph = GraphAPI(self.access_token)
        profile = graph.get_object(self.user)
        api_posts = graph.get_connections(profile['id'], 'posts')
        posts = []

        for api_post in api_posts['data']:
            insights_path = '/v2.3/%s/insights/' % api_post['id']
            insights = graph.request(insights_path)
            posts.append(Post(api_post, insights, self.run_time))

        return posts

    def write(self, db, posts):
        """
        Write to database
        """
        # table = db['homepage']
        #
        # for article, api_entry in zip(articles, api_entries):
        #     row = article.serialize()
        #     row.update(api_entry.serialize())
        #     table.insert(row)
        pass
