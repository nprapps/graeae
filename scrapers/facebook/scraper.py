#!/usr/bin/env python

from datetime import datetime
import json

from facebook import GraphAPI

from app_config import get_secrets
from models import Post, Insights

SECRETS = get_secrets()

class FacebookScraper:
    access_token = SECRETS['FACEBOOK_TOKEN']
    user = 'NPR'

    def __init__(self):
        self.run_time = datetime.utcnow()
        self.graph = GraphAPI(self.access_token)

    def scrape_facebook(self, profile_filename=None, posts_filename=None):
        """
        Scrape!
        """
        if profile_filename:
            with open(profile_filename) as f:
                profile = json.load(f)
        else:
            profile = self.graph.get_object(self.user)

        # with open('tests/snapshots/fb-profile-04-20-2015.json', 'w') as f:
        #     f.write(json.dumps(profile))

        if posts_filename:
            with open(posts_filename) as f:
                api_posts = json.load(f)
        else:
            api_posts = self.graph.get_connections(profile['id'], 'posts')

        # with open('tests/snapshots/fb-posts-04-20-2015.json', 'w') as f:
        #     f.write(json.dumps(api_posts))

        posts = []

        for api_post in api_posts['data']:
            posts.append(Post(api_post, self.run_time))

        return posts

    def scrape_insights(self, posts):
        insights = []

        for post in posts:
            insights.append(self.scrape_post_insights(post))

        return insights

    def scrape_post_insights(self, post, filename=None):
        if filename:
            with open(filename) as f:
                api_insights = json.load(f)
        else:
            api_insights = self.graph.get_object('%s/insights/' % post.id)

        # with open('tests/snapshots/fb-insights-04-20-2015.json', 'w') as f:
        #     f.write(json.dumps(api_insights))

        return Insights(post, api_insights)

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
