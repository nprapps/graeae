import app_config

from datetime import datetime, timedelta
from oauth import get_credentials
from scrapers.google_analytics.models import GoogleAnalyticsRow

import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GoogleAnalyticsScraper:
    def __init__(self):
        self.run_time = datetime.utcnow()

    def scrape_google_analytics(self, start_date, end_date):
        delta = timedelta(days=1)
        rows = []

        api_url = 'https://www.googleapis.com/analytics/v3/data/ga'
        credentials = get_credentials()

        metrics = ','.join(['ga:{0}'.format(metric) for metric in app_config.GA_METRICS])
        dimensions = ','.join(['ga:{0}'.format(dimensions) for dimensions in app_config.GA_DIMENSIONS])

        query_date = start_date

        params = {
            'ids': 'ga:{0}'.format(app_config.GA_ORGANIZATION_ID),
            'start-date': query_date.strftime('%Y-%m-%d'),
            'end-date': query_date.strftime('%Y-%m-%d'),
            'metrics': 'ga:sessions,ga:pageviews',
            'dimensions': 'ga:pagePath,ga:source,ga:deviceCategory',
            'max-results': app_config.GA_RESULT_SIZE,
            'samplingLevel': app_config.GA_SAMPLING_LEVEL,
            'sort': '-ga:pageviews',
        }

        while True:
            if query_date == end_date:
                print "Stopping at {0}".format(params['start-date'])
                break

            logger.info('Getting analytics for {0}'.format(params['start-date']))
            resp = app_config.authomatic.access(credentials, api_url, params=params)

            #import ipdb; ipdb.set_trace();

            if resp.status != 200:
                logger.warn('Analytics API responded with status code {0}, stopping. (Message - {1})'.format(resp.status, resp.data['error']['message']))
                break

            for row in resp.data['rows']:
                analytics_row = GoogleAnalyticsRow(row, query_date, app_config.GA_METRICS, app_config.GA_DIMENSIONS)
                rows.append(analytics_row.serialize())

            query_date += delta
            params['start-date'] = query_date.strftime('%Y-%m-%d')
            params['end-date'] = params['start-date']

        #import ipdb; ipdb.set_trace();
        return rows

    def write(self, db, rows):
        table = db['google_analytics']
        table.delete()
        table.insert_many(rows)
