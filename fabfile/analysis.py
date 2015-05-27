import dataset
import app_config
from fabric.api import task

@task
def get_insights():
	"""
	gets insights and writes csv
	"""
	db = dataset.connect(app_config.POSTGRES_URL)
	result = db.query("""
	select f1.*
		from facebook f1
		inner join
			(select link_url, max(run_time) as max_run_time from facebook group by link_url) f2 
			on f1.link_url = f2.link_url and f1.run_time = f2.max_run_time
			""")
	dataset.freeze(result, format='csv', filename='output/insights.csv')

@task
def get_insights_and_art():
	"""
	gets insights and art and writes csv
	"""
	db = dataset.connect(app_config.POSTGRES_URL)
	result = db.query("""
	select f1.*, s.has_lead_art, s.lead_art_provider, s.lead_art_url, s.title, s.story_id
		from facebook f1
		inner join
			(select link_url, max(run_time) as max_run_time from facebook group by link_url) f2 
			on f1.link_url = f2.link_url and f1.run_time = f2.max_run_time
		join 
			seamus s
			on f1.link_url = s.canonical_url
			""")
	dataset.freeze(result, format='csv', filename='output/insights_and_art.csv')



