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
	result_list = list(result)
	for row in result_list:
		row['provider_category'] = _get_provider_category(row)
		row['provider_type'] = _get_provider_type(row)
		row['post_url'] = _make_post_url(row)

	dataset.freeze(result_list, format='csv', filename='output/insights_and_art.csv')

def _get_provider_category(row):
	"""
	determine provider category from lead art provider
	"""
	if row['lead_art_provider']:
		if 'courtesy of' in row['lead_art_provider'].lower():
			return 'Courtesy'
		elif 'for npr' in row['lead_art_provider'].lower():
			return 'For NPR'
		else:
			return row['lead_art_provider']
	else:
		return None

def _get_provider_type(row):
	"""
	groups provider by type
	"""
	if row['provider_category']:
		if 'npr' in row['provider_category'].lower():
			return 'NPR'
		elif 'getty' in row['provider_category'].lower() or 'istock' in row['provider_category'].lower() or 'corbis' in row['provider_category'].lower():
			return 'Stock'
		elif 'AP' in row['provider_category']:
			return 'Wire'
		else:
			return 'Other'
	else:
		return None

def _make_post_url(row):
	"""
	create the facebook post URL from ID
	"""
	post_url = "http://facebook.com/{0}".format(row['facebook_id'])
	return post_url
	
