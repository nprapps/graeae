import datetime

from collections import OrderedDict

class Story:
    """
    Represent a story we worked on
    """
    def __init__(self, story):
        self.story = story

    def serialize(self):
        return OrderedDict([
            ('seamus_id', self.seamus_id),
            ('timestamp', self.timestamp),
            ('duration', self.duration),
            ('contributors', self.contributors),
            ('contribution', self.contribution),
        ])

    @property
    def timestamp(self):
        seconds = (float(self.story['Timestamp']) - 25569) * 86400.0
        return datetime.datetime.utcfromtimestamp(seconds)

    @property
    def seamus_id(self):
        return self.story['Seamus ID']

    @property
    def contribution(self):
        return self.story['What did you do?']

    @property
    def contributors(self):
        contributors = [contributor.strip() for contributor in self.story['Who worked on it?'].split(',')]
        return contributors

    @property
    def duration(self):
        value = self.story['How long did it take? (hours)']
        if value:
            return abs(float(value))
        else:
            return 0

