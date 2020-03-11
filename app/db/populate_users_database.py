import csv, bcrypt, mysql.connector, uuid
import os
from argparse import ArgumentParser
from getpass import getpass

"""
Populate database with pre-made usernames and passwords stored in users.txt.
Used to initially populate database where usernames and passwords that will be given individually to each user. 
Once the user has logged in they will then be asked to change their password.
"""

def gen_random_password():
    return uuid.uuid4().hex

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

    try:
        if not os.path.exists('app/db/user_first_time_passwords.csv'):
                with open('app/db/user_first_time_passwords.csv', 'w'): pass
    except:
        if not os.path.exists('db/user_first_time_passwords.csv'):
            with open('db/user_first_time_passwords.csv', 'w'): pass

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

    # if user hasn't entered a password in command line
    if args.adminpass == "":
        admin_password = getpass("Enter admin password: ").encode('utf-8')
    else:
        admin_password = args.adminpass.encode('utf-8')

    hashed_password = bcrypt.hashpw(admin_password, bcrypt.gensalt())

    mycursor = mydb.cursor()

    mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("admin", hashed_password))

    with open("app/db/user_first_time_passwords.csv", 'a') as f:
        f.write("admin" + ',' + str(admin_password) + '\n')

    with open('app/db/users.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        for row in spamreader:
            username = row[0]
            course = row[1]
            year = row[2]
            password = gen_random_password().encode('utf-8')

            with open("app/db/user_first_time_passwords.csv", 'a') as f:
                f.write(str(username) + ',' + str(password) + '\n')

            print("EMAIL (in production):", username, password)

            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

            mycursor = mydb.cursor()

            mycursor.execute("INSERT INTO users (username, password, course, year) VALUES (%s, %s, %s, %s)", (username, hashed_password, course, year))

        mydb.commit()

