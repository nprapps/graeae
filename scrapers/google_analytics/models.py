from collections import OrderedDict
from scrapers.utils import get_seamus_id_from_url

class GoogleAnalyticsRow:

    def __init__(self, row, metrics, dimensions, meta):
        self.row = row
        self.fields = dimensions + metrics

        data = OrderedDict(zip(self.fields, self.row))
        new_data = OrderedDict()
        for k, v in data.items():
            if v.isnumeric():
                new_data[k.lower()] = float(v)
            else:
                new_data[k.lower()] = v

        self.data = new_data

    def serialize(self):
        self.data['story_id'] = self.story_id
        return self.data

    @property
    def story_id(self):
        full_path = u'http://www.npr.org{0}'.format(self.data['pagepath'])
        return get_seamus_id_from_url(full_path)

