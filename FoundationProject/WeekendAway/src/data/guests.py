import datetime
import mongoengine


class Guests(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'guests'
    }
