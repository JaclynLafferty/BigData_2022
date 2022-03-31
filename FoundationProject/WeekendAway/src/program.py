from turtle import home
from colorama import Fore
import program_guests
import program_hosts
from pymongo import MongoClient
import data.mongoSetup as mongoSetup


def main():
    mongoSetup.global_init()

    print_header()

    try:
        while True:
            if find_user_intent() == 'book':
                program_guests.run()
            else:
                program_hosts.run()
    except KeyboardInterrupt:
        return


def print_header():
    #home = \
        #"""
        #Possible Picture
        #"""
    
    print(Fore.WHITE + '****************  Weekend Away  ****************')
    print()
    #print(Fore.GREEN + home)
    print(Fore.WHITE + '************************************************')
    print()
    print("Welcome to Weekend Away!")
    print("Why are you here?")
    print()


def find_user_intent():
    print("[g] Book a home for a stay.")
    print("[h] Offer your home for a stay.")
    print()
    choice = input("Are you a [g]uest or [h]ost? ")
    if choice == 'h':
        return 'offer'

    return 'book'


if __name__ == '__main__':
    main()
