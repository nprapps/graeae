import dataset
import app_config
import csv
# import unicodecsv as csv
from fabric.api import task
from journalism import Table, TextType, NumberType, DateType, BooleanType

text_type = TextType()
number_type = NumberType()
date_type = DateType()
boolean_type = BooleanType()

@task(default=True)
def analyse():
    """
    Run the full analysis suite
    """
    get_raw_insights()
    get_insights()
    analyse_insights()

@task
def get_raw_insights():
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

    dataset.freeze(result_list, format='csv', filename='www/live-data/insights_raw.csv')

@task
def get_insights():
    """
    gets insights for summary
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    result = db.query("""
    select f1.created_time, f1.people_reached, f1.shares, f1.likes, f1.comments, f1.link_clicks, s.has_lead_art, s.lead_art_provider
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

    dataset.freeze(result_list, format='csv', filename='www/live-data/insights.csv')

@task
def analyse_insights():
    """
    generate reports from insights data
    """
    column_types = (date_type, number_type, number_type, number_type, number_type, number_type, boolean_type, text_type, text_type, text_type)

    with open('www/live-data/insights.csv') as f:
        rows = list(csv.reader(f))

    column_names = rows.pop(0)

    table = Table(rows, column_types, column_names)

    summary_definition = (
        ('likes', 'sum'),
        ('comments', 'sum'),
        ('shares', 'sum'),
        ('people_reached', 'sum')
    )

    summary = table.aggregate('provider_type', summary_definition)

    for column_name, aggregation_function in summary_definition:
        computed_name = '{0}_{1}'.format(column_name, aggregation_function)
        normalized_name = 'normalized_{0}'.format(column_name)
        summary = summary.compute(normalized_name, number_type,
            lambda row: row[computed_name] / row['provider_type_count'])

    with open('www/live-data/insights_summary.csv', 'w') as f:
        writer = csv.writer(f)

        writer.writerow(summary.get_column_names())
        writer.writerows(summary.rows)

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
    
