import csv
from datetime import datetime

import MySQLdb.cursors


class db:

    def __init__(self, mysql, bcrypt, cards_dict):
        self.mysql = mysql
        self.bcrypt = bcrypt
        self.cards_dict = cards_dict

    def successful_login(self, username, password, gdpr_consent=None):
        """
        Can user login

        :param username: username string
        :param password: plain text password
        :param gdpr_consent: "concent" or anything else
        :return: None if successful else a message
        """

        # For reference: https://codeshack.io/login-system-python-flask-mysql/
        if gdpr_consent != 'consent' and gdpr_consent != None:
            msg = "Check GDPR consent to continue"
            return msg

        # Check if account exists using MySQL
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute('SELECT password FROM users WHERE username = %s', (username,)):
            # Fetch one record and return result
            password_hash = cursor.fetchone()['password']
        # If command fails, Clearly no username %s match
        else:
            msg = "User account does not exist"
            return msg

        authenticated_user = self.bcrypt.check_password_hash(password_hash, password)
        if authenticated_user:
            # Redirect to home page
            return None
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return msg

    def get_all_users(self):
        """
        Get all users
        :return: list of users. [] if nothing found
        """
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # If command fails. Clearly no username %s match
        if cursor.execute('SELECT * FROM users'):
            # Fetch record and return result
            users = cursor.fetchall()
            return users
        else:
            return []

    def get_num_of_active_players(self):
        """
        Get number of players that own a card, so active in game
        :return: int
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # If command fails, don't bother with the rest. Clearly no username %s match
        if cursor.execute('SELECT COUNT(username) FROM won'):
            # Fetch one record and return result
            num_users = cursor.fetchall()
            return num_users[0]['COUNT(username)']
        else:
            return 0

    def get_all_won_cards(self):
        """
        Get completed cards
        :return: list of cards. [] if nothing found
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # If command fails, don't bother with the rest. Clearly no username %s match
        if cursor.execute('SELECT * FROM won'):
            # Fetch record and return result
            wons = cursor.fetchall()
            return wons
        else:
            return []

    def get_overall_progress(self):
        """
        Get overall progress
        :return: num between 0 and 100%
        """

        won_cards = self.get_all_won_cards()
        users = self.get_all_users()

        return (len(won_cards) * 100) / (len(users) * len(self.cards_dict))

    def get_overall_progress_over_time(self):
        """
        Get overall progress over time.
        :return: list of tuples. (progress score, timestamp)
        """
        progress = [tuple(row) for row in csv.reader(open("app/db/progress.csv", 'rU'))]

        return progress

    def won_card_distribution(self):
        """
        Get num of owned cards at locations
        :return: list of cardLocation, COUNT(*)
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute('SELECT cardLocation, COUNT(*) FROM won GROUP BY cardLocation'):
            distribution = list(cursor.fetchall())
            return distribution
        else:
            return []

    def top_locations_by_playerbase_ownership(self):
        """
        Get location by percentage of players that own the location
        :return: dict. location : %
        """

        won_cards = self.won_card_distribution()
        percentage_complete = {}
        for card in won_cards:
            percentage_complete[card['cardLocation']] = (card['COUNT(*)'] * 100) / len(self.get_all_users())

        return sorted(percentage_complete.items(), key=lambda x: x[1], reverse=True)

    def get_won_cards_by_user(self, username):
        """
        Get owned cards by session user
        :return: list of locations(cards). [] if nothing found
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute('SELECT cardLocation FROM won WHERE username = %s', (username,)):
            locations = [item['cardLocation'] for item in cursor.fetchall()]
            return locations
        else:
            return []

    def add_won_card(self, username, location):
        """
        Add completed card entry to won db

        :param username: string
        :param location: string card location
        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor.execute('INSERT INTO won (username, cardLocation, timeStamp) VALUES (%s, %s, %s)',
                           (username, location, timestamp))
        except:
            return False

        self.mysql.connection.commit()
        return True

    def reset_my_cards(self, username):
        """
        Removes all owned and completed cards from won db

        :param username: string
        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute('DELETE FROM won WHERE username=%s', (username,))
        except:
            return False

        self.mysql.connection.commit()
        return True

    def get_all_help_requests(self):
        """
        Get all help requests from players
        :return: list of help requests. [] if nothing found
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if cursor.execute('SELECT * FROM helpRequests ORDER BY open DESC'):
            help_reqs = cursor.fetchall()
            return help_reqs
        else:
            return []

    def get_num_of_open_help_requests(self):
        """
        Get number of help requests
        :return: int
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if cursor.execute('SELECT COUNT(*) FROM helpRequests WHERE open=1'):
            num_users = cursor.fetchall()
            return num_users[0]['COUNT(*)']
        else:
            return 0

    def get_help_requests_by_user(self, username):
        """
        Get all help requests by given user
        :return: list of help requests. [] if nothing found
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if cursor.execute('SELECT * FROM helpRequests WHERE username = %s ORDER BY open DESC', (username,)):
            help_reqs = cursor.fetchall()
            return help_reqs
        else:
            return []

    def add_help_request(self, username, description):
        """
        Add user help request to db

        :param username: string
        :param description: string
        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor.execute('INSERT INTO helpRequests (username, open, description, timeStamp) VALUES (%s, %s, %s, %s)',
                           (username, 1, description, timestamp))
        except:
            return False

        self.mysql.connection.commit()
        return True

    def open_help_request(self, username, id):
        """
        Opens help request in db

        :param id: int
        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if username != "admin":
            try:
                # does the user own the help req id
                cursor.execute('SELECT id, username FROM helpRequests WHERE id=%s and username = %s', (id, username))
                if len(list(cursor.fetchall())) == 0:
                    return False
            except:
                return False

        try:
            cursor.execute('UPDATE helpRequests SET open = 1 WHERE id=%s', (id,))
        except:
            return False

        self.mysql.connection.commit()
        return True

    def close_help_request(self, username, id):
        """
        Close help request in db

        :param id: int
        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if username != "admin":
            try:
                # does the user own the help req id
                cursor.execute('SELECT id, username FROM helpRequests WHERE id=%s and username = %s', (id, username))
                if len(list(cursor.fetchall())) == 0:
                    return False
            except:
                return False

        try:
            cursor.execute('UPDATE helpRequests SET open = 0 WHERE id=%s', (id,))
        except:
            return False

        self.mysql.connection.commit()
        return True

    def remove_help_request(self, id):
        """
        Removes help request from database

        :param id: id number
        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute('DELETE FROM helpRequests WHERE id=%s', (id,))
        except:
            return False

        self.mysql.connection.commit()
        return True

    def reset_won_db(self):
        """
        Removes all rows from won db

        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute('DELETE FROM won')
        except:
            return False

        self.mysql.connection.commit()
        return True

    def reset_users_db(self):
        """
        Removes all rows from users db

        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute('DELETE FROM users')
        except:
            return False

        self.mysql.connection.commit()
        return True

    def reset_help_requests_db(self):
        """
        Removes all rows from help requests db

        :return: True if successful, else false
        """

        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        try:
            cursor.execute('DELETE FROM helpRequests')
        except:
            return False

        self.mysql.connection.commit()
        return True
