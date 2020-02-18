#!/usr/bin/python3

from argparse import ArgumentParser
from getpass import getpass

from exeter_treasure_hunt import app

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--dbhost", type=str,
                        help="mysql host name e.g db or localhost", required = False, default = "localhost")
    parser.add_argument("-p", "--dbpassword", type=str,
                        help="root password for db", required = False, default = "")

    args = parser.parse_args()

    app.config['MYSQL_HOST'] = args.dbhost
    app.config['MYSQL_PASSWORD'] = args.dbpassword

    # if user hasn't entered a password in command line
    if args.dbpassword == "":
        password = getpass("Enter root@" + args.dbhost + " password: ")
        app.config['MYSQL_PASSWORD'] = password
    else:
        app.config['MYSQL_PASSWORD'] = args.dbpassword

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
