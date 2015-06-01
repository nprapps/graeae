import copytext
from models import Story

class SpreadsheetScraper:
    """
    Scrape the NPR Visuals 'did we touch it?' spreadsheet
    """
    def scrape_spreadsheet(self, spreadsheet_filename):
        stories = []
        spreadsheet = copytext.Copy(spreadsheet_filename)
        data = spreadsheet['Form Responses 1']
        for row in data:
            story = Story(row)
            stories.append(story)
        return stories

    def write(self, db, stories):
        table = db['spreadsheet']
        for story in stories:
            table.upsert(story.serialize(), ['seamus_id'])
