#!/usr/bin/env python

from scrapers.homepage import HomepageScraper

if __name__ == '__main__':
    homepage_scraper = HomepageScraper()
    homepage_scraper.scrape()
