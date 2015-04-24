#!/usr/bin/env python

from datetime import datetime
import json
import logging

from facebook import GraphAPI

from app_config import get_secrets
from models import Post, Insights

SECRETS = get_secrets()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookScraper:
    access_token = SECRETS['FACEBOOK_TOKEN']
    user = 'NPR'

    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_facebook(self, profile_filename=None, posts_filename=None):
        """
        Scrape!
        """
        logger.info('Scraping Facebook (start time: %s)' % self.run_time)

        if profile_filename and posts_filename:
            with open(profile_filename) as f:
                profile = json.load(f)

            with open(posts_filename) as f:
                api_posts = json.load(f)
        else:
            self.graph = GraphAPI(self.access_token)

            profile = self.graph.get_object(self.user)
            api_posts = self.graph.get_connections(profile['id'], 'posts')

        # with open('tests/snapshots/fb-profile-04-20-2015.json', 'w') as f:
        #     f.write(json.dumps(profile))

        # with open('tests/snapshots/fb-posts-04-20-2015.json', 'w') as f:
        #     f.write(json.dumps(api_posts))

        posts = []

        for api_post in api_posts['data']:
            post = Post(api_post, self.run_time)
            posts.append(post)
            logger.info('Scraped basic information for %s from Facebook (%s)' % (post.id, post.headline))

        return posts

    def scrape_insights(self, posts):
        insights = []

        for post in posts:
            insight = self.scrape_post_insights(post)
            insights.append(insight)
            logger.info('Scraped insights for %s from Facebook (%s)' % (post.id, post.headline))

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

    def write(self, db, posts, insights):
        """
        Write to database
        """
        table = db['facebook']

        for post, insight in zip(posts, insights):
            row = post.serialize()
            row.update(insight.serialize())
            table.insert(row)
