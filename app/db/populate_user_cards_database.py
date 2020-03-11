import csv, mysql.connector
import json
from argparse import ArgumentParser
from getpass import getpass
import random
"""

"""

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--dbhost", type=str,
                        help="mysql host name e.g db or localhost", required=False, default="localhost")
    parser.add_argument("-u", "--dbuser", type=str,
                        help="mysql username, ie root", required=False, default="root")
    parser.add_argument("-p", "--dbpassword", type=str,
                        help="root password for db", required=False, default="")
    parser.add_argument("-n", "--dbname", type=str,
                        help="mysql database name, ie ETH_DATABASE", required=False, default="ETH_DATABASE")
    parser.add_argument("-t", "--port", type=str,
                        help="mysql port", required=False, default="3306")
    parser.add_argument("-q", "--adminpass", type=str,
                        help="admin password for db", required=False, default="")

    args = parser.parse_args()

    # if user hasn't entered a password in command line
    if args.dbpassword == "":
        password = getpass("Enter root@" + args.dbhost + " password: ")
        db_password = password
    else:
        db_password = args.dbpassword

    mydb = mysql.connector.connect(
        host=args.dbhost,
        user=args.dbuser,
        passwd=db_password,
        port=args.port,
        database=args.dbname,
        auth_plugin='mysql_native_password'
    )


    mycursor = mydb.cursor()

    try:
        with open('app/db/cards.json', 'r') as f:
            cards_dict = json.load(f)
    except:
        with open('db/cards.json', 'r') as f:
            cards_dict = json.load(f)

    locations = []
    for card in cards_dict:
        locations.append(card['location'])

    with open('app/db/users.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        for row in spamreader:
            username = row[0]

            random_locations_for_user = []

            for i in range(3):
                random_location = ""
                while random_location in random_locations_for_user or random_location == "":
                    random_location = random.choice(locations)

                random_locations_for_user.append(random_location)
                print(username, random_location)

                mycursor.execute("INSERT INTO userCards (username, cardLocation, state) VALUES (%s, %s, 'uncompleted')", (username, random_location))

        mydb.commit()

