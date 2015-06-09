import dataset
import app_config
import csv
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
    print 'Analysing ALL the data'
    get_raw_insights()
    get_insights()
    analyse_insights()
    get_photo_efforts()
    analyse_photo_efforts()

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
        ('likes', 'median'),
        ('likes', 'mean'),
        ('comments', 'sum'),
        ('comments', 'median'),
        ('comments', 'mean'),
        ('shares', 'sum'),
        ('shares', 'median'),
        ('shares', 'mean'),
        ('people_reached', 'sum'),
        ('people_reached', 'median'),
        ('people_reached', 'mean'),
    )

    summary = table.aggregate('provider_type', summary_definition)

    count_grand_total = summary.columns['provider_type_count'].sum()
    summary = summary.compute('provider_type_count_pct', number_type,
        lambda x: (x['provider_type_count']/count_grand_total) * 100)

    _write_summary_csv(summary, 'www/live-data/insights_summary.csv')

@task
def get_photo_efforts():
    """
    Get did we touch it db combined with homepage db
    """
    db = dataset.connect(app_config.POSTGRES_URL)
    result = db.query("""
        select s.duration, s.contribution, s.seamus_id, hp.url
        from homepage hp
        inner join
            (select story_id, max(run_time) as max_run_time from homepage group by story_id) hp2
            on hp.story_id = hp2.story_id and hp.run_time = hp2.max_run_time
        right join
            spreadsheet s
            on hp.story_id = s.seamus_id
    """)
    result_list = list(result)
    for row in result_list:
        row['on_homepage'] = (row['url'] != None)

    dataset.freeze(result_list, format='csv', filename='www/live-data/photo_efforts.csv')

@task
def analyse_photo_efforts():
    column_types = (number_type, text_type, text_type, text_type, boolean_type)

    with open('www/live-data/photo_efforts.csv') as f:
        rows = list(csv.reader(f))

    column_names = rows.pop(0)
    table = Table(rows, column_types, column_names)

    homepage_summary = table.aggregate('on_homepage', (('duration', 'sum'),))

    count_grand_total = homepage_summary.columns['on_homepage_count'].sum()
    homepage_summary = homepage_summary.compute('on_homepage_count_pct', number_type,
        lambda x: (x['on_homepage_count']/count_grand_total) * 100)

    count_grand_total = homepage_summary.columns['duration_sum'].sum()
    homepage_summary = homepage_summary.compute('duration_sum_pct', number_type,
        lambda x: (x['duration_sum']/count_grand_total) * 100)

    _write_summary_csv(homepage_summary, 'www/live-data/homepage_summary.csv')

    contribution_summary = table.aggregate('contribution', (('duration', 'sum'),))
    contribution_summary = contribution_summary.order_by('contribution_count', reverse=True)
    contribution_summary = contribution_summary.compute('contribution_count_pct', number_type,
        lambda x: (x['contribution_count']/count_grand_total) * 100)

    contribution_summary = contribution_summary.compute('duration_sum_pct', number_type,
        lambda x: (x['duration_sum']/count_grand_total) * 100)

    _write_summary_csv(contribution_summary, 'www/live-data/contribution_summary.csv')

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
        elif 'getty' in row['provider_category'].lower():
            return 'Getty'
        elif 'istock' in row['provider_category'].lower():
            return 'iStock'
        elif 'corbis' in row['provider_category'].lower():
            return 'Corbis'
        elif 'AP' in row['provider_category'] or 'landov' in row['provider_category'].lower():
            return 'Wire'
        elif row['provider_category'] == 'Courtesy':
            return 'Courtesy'
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

def _write_summary_csv(table, path):
    """
    create csv with grand totals
    """
    with open(path, 'w') as f:
        writer = csv.writer(f)

        writer.writerow(table.get_column_names())
        writer.writerows(table.rows)

        grand_totals_row = []
        for i, column_name in enumerate(table.get_column_names()):
            column = table.columns[column_name]
            if i == 0:
                grand_totals_row.append('Grand total')
            else:
                grand_totals_row.append(column.sum())

        writer.writerow(grand_totals_row)
    
