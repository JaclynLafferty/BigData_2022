from cgi import print_exception
from subprocess import IDLE_PRIORITY_CLASS
from turtle import home
from typing import List, Optional

import datetime
from unicodedata import name
from xml.sax.handler import feature_external_ges

import bson
from numpy import delete

from data.bookings import Bookings
from data.homes import Homes
from data.owners import Owners
from data.guests import Guests


def create_account(name: str, email: str) -> Owners:
    owner = Owners()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owners:
    owner = Owners.objects(email=email).first()
    return owner

def register_home(active_account: Owners, 
    name, feet, price) -> Homes:
    home = Homes()

    home.name = name
    home.square_feet = feet
    home.price = price

    home.save()

    account = find_account_by_email(active_account.email)
    account.home_ids.append(home.id)
    account.save()

    return home


def find_homes_for_user(account: Owners) -> List[Homes]:
    query = Homes.objects(id__in = account.home_ids)
    homes = list(query)

    return homes


def add_available_date(home: Homes,
                       start_date: datetime.datetime, days: int) -> Homes:
    booking = Bookings()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    home = Homes.objects(id=home.id).first()
    home.bookings.append(booking)
    home.save()

    return home


def add_guest(account, name) -> Guests:
    guest = Guests()
    guest.name = name
    guest.save()

    owner = find_account_by_email(account.email)
    owner.guest_ids.append(guest.id)
    owner.save()

    return guest


def get_guests_for_user(user_id: bson.ObjectId) -> List[Guests]:
    owner = Owners.objects(id=user_id).first()
    guests = Guests.objects(id__in=owner.guest_ids).all()

    return list(guests)


def get_available_homes(checkin: datetime.datetime,
                        checkout: datetime.datetime, guest: Guests) -> List[Homes]:
    
    query = Homes.objects() \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    homes = query.order_by('price', '-square_feet')

    final_homes = []
    for c in homes:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_guest_id is None:
                final_homes.append(c)

    return final_homes


def book_home(account, guest, home, checkin, checkout):
    booking: Optional[Bookings] = None

    for b in home.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_owner_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_guest_id = guest.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    home.save()


def get_bookings_for_user(email: str) -> List[Bookings]:
    account = find_account_by_email(email)

    booked_homes = Homes.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_home_to_booking(home, booking):
        booking.home = home
        return booking

    bookings = [
        map_home_to_booking(home, booking)
        for home in booked_homes
        for booking in home.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
