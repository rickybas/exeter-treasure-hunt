# !/usr/bin/python3

from argparse import ArgumentParser
from getpass import getpass
import os

from exeter_treasure_hunt import app

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

    args = parser.parse_args()

    # Database config
    app.config['MYSQL_HOST'] = args.dbhost
    app.config['MYSQL_PASSWORD'] = args.dbpassword
    app.config['MYSQL_PORT'] = 3306
    app.config['MYSQL_USER'] = args.dbuser
    app.config['MYSQL_DB'] = args.dbname

    # if user hasn't entered a password in command line
    if args.dbpassword == "":
        password = getpass("Enter root@" + args.dbhost + " password: ")
        app.config['MYSQL_PASSWORD'] = password
    else:
        app.config['MYSQL_PASSWORD'] = args.dbpassword

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, ssl_context='adhoc')
