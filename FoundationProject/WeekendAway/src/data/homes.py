import datetime
import mongoengine

from data.bookings import Bookings


class Homes(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    square_feet = mongoengine.FloatField(required=True)
    bookings = mongoengine.EmbeddedDocumentListField(Bookings)

    meta = {
        'db_alias': 'core',
        'collection': 'homes'
    }
