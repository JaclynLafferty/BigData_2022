import datetime
from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import services.data_service as svc
from program_hosts import success_msg, error_msg
import infrastructure.state as state


def run():
    print(' ****************** Welcome Guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)
            s.case('a', add_a_guest)
            s.case('y', view_your_guests)
            s.case('b', book_a_home)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'Bye', 'Exit', 'Exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a home')
    print('[A]dd a guest')
    print('View [y]our guests')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_guest():
    print(' ****************** Add A Guest **************** ')
    if not state.active_account:
        error_msg("You must log in first to add a guest.")
        return

    name = input("What is your guest's name? ")
    if not name:
        error_msg('cancelled')
        return

    guest = svc.add_guest(state.active_account, name)
    state.reload_account()
    success_msg('Created {} with id {}'.format(guest.name, guest.id))


def view_your_guests():
    print(' ****************** Your Guests **************** ')
    if not state.active_account:
        error_msg("You must log in first to view your guests.")
        return

    guests = svc.get_guests_for_user(state.active_account.id)
    print("You have {} guests.".format(len(guests)))
    for s in guests:
        print(" * {}.".format(
            s.name,
        ))


def book_a_home():
    print(' ****************** Book A Home **************** ')
    if not state.active_account:
        error_msg("You must log in first to book a home.")
        return

    guests = svc.get_guests_for_user(state.active_account.id)
    if not guests:
        error_msg('You must first [a]dd a guest before you can book a home.')
        return

    print("Let's start by finding available homes.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")
    if not start_text:
        error_msg('cancelled')
        return

    checkin = parser.parse(
        start_text
    )
    checkout = parser.parse(
        input("Check-out date [yyyy-mm-dd]: ")
    )
    if checkin >= checkout:
        error_msg('Check in must be before check out.')
        return

    print()
    for idx, s in enumerate(guests):
        print('{}. {} '.format(
            idx + 1,
            s.name,
        ))

    guest = guests[int(input('Which guest do you want to book (number)? ')) - 1]

    homes = svc.get_available_homes(checkin, checkout, guest)

    print("There are {} homes available in that time.".format(len(homes)))
    for idx, c in enumerate(homes):
        print(" {}. {} with {} square feet.".format(
            idx + 1,
            c.name,
            c.square_feet
            ))

    if not homes:
        error_msg("Sorry, no homes are available for that date.")
        return

    home = homes[int(input('Which home do you want to book (number)? ')) - 1]
    svc.book_home(state.active_account, guest, home, checkin, checkout)

    success_msg('Successfully booked {} for {} at ${}/night.'.format(home.name, guest.name, home.price))


def view_bookings():
    print(' ****************** Your Bookings **************** ')
    if not state.active_account:
        error_msg("You must log in first to register a home.")
        return

    guests = {s.id: s for s in svc.get_guests_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print("You have {} bookings.".format(len(bookings)))
    for b in bookings:
        print(' * Guest: {} is booked at {} from {} for {} days.'.format(
            guests.get(b.guest_guest_id).name,
            b.home.name,
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            (b.check_out_date - b.check_in_date).days
        ))
