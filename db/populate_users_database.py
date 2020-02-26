import csv, bcrypt, mysql.connector
from argparse import ArgumentParser
from getpass import getpass

"""
Populate database with pre-made usernames and passwords stored in users.txt.
Used to initially populate database where usernames and passwords that will be given individually to each user. 
Once the user has logged in they will then be asked to change their password.
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
                        help="mysql database name, ie USERS_DATABASE", required=False, default="USERS_DATABASE")

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
        port=3306,
        database=args.dbname,
        auth_plugin='mysql_native_password'
    )

    with open('db/users.txt', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            username = row[0]
            password = row[1].encode('utf-8')

            print(username, password)

            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            mycursor = mydb.cursor()

            mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))

        mydb.commit()
