import datetime
from colorama import Fore
from dateutil import parser

from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome Host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', create_account)
            s.case('l', log_into_account)
            #s.case('d', delete_host)
            s.case('y', list_homes)
            s.case('r', register_home)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'Bye', 'Exit', 'Exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an [a]ccount')
    print('[L]ogin to your account')
    print('[D]elete your account')
    print('List [y]our home')
    print('[R]egister a home')
    print('[U]pdate home availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** Register **************** ')

    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    state.active_account = svc.create_account(name, email)
    success_msg(f"Created new account with id {state.active_account.id}.")


def log_into_account():
    print(' ****************** Login **************** ')

    email = input('What is your email? ').strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f'Could not find account with email {email}.')
        return

    state.active_account = account
    success_msg('Logged in successfully.')

    
def register_home():
    print(' ****************** Register A Home **************** ')

    if not state.active_account:
        error_msg('You must login first to register a home.')
        return

    square_feet = input('How many square feet is the home? ')
    if not square_feet:
        error_msg('Cancelled')
        return

    
    square_feet = float(square_feet)
    name = input("Give your home a name: ")
    price = float(input("How much are you charging?  "))

    home = svc.register_home(
        state.active_account, name, square_feet, price)

    state.reload_account()
    success_msg(f'Registered a new home with id {home.id}.')


def list_homes(suppress_header=False):
    if not suppress_header:
        print(' ******************     Your Homes     **************** ')

    if not state.active_account:
        error_msg('You must login first to register a home.')
        return

    homes = svc.find_homes_for_user(state.active_account)
    print(f"You have {len(homes)} homes.")
    for idx, c in enumerate(homes):
        print(f' {idx + 1}.  {c.name} is {c.square_feet} square feet.')
        for b in c.bookings:
            print('      * Booking: {}, {} days, booked? {}'.format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'
            ))


def update_availability():
    print(' ****************** Add Available Dates **************** ')

    if not state.active_account:
        error_msg("You must log in first to register a home.")
        return

    list_homes(suppress_header=True)

    home_number = input("Enter home number: ")
    if not home_number.strip():
        error_msg('Cancelled')
        print()
        return

    home_number = int(home_number)

    homes = svc.find_homes_for_user(state.active_account)
    selected_home = homes[home_number - 1]

    success_msg("Selected home {}".format(selected_home.name))

    start_date = parser.parse(
        input("Enter available date [yyyy-mm-dd]: ")
    )
    days = int(input("How many days is this block of time? "))

    svc.add_available_date(
        selected_home,
        start_date,
        days
    )

    success_msg(f'Date added to home {selected_home.name}.')


def view_bookings():
    print(' ****************** Your Bookings **************** ')

    if not state.active_account:
        error_msg("You must log in first to register a home.")
        return

    homes = svc.find_homes_for_user(state.active_account)

    bookings = [
        (c, b)
        for c in homes
        for b in c.bookings
        if b.booked_date is not None
    ]

    print("You have {} bookings.".format(len(bookings)))
    for c, b in bookings:
        print(' * Home: {}, Booked Date: {}, from {} for {} days.'.format(
            c.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))


def exit_app():
    print()
    print('Bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '
    
    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
