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

