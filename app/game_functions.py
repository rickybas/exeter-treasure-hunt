import os

import MySQLdb


class GameFunctions:

    def __init__(self, mysql):
        self.mysql = mysql

    def stop_game(self):
        wr = open("app/db/state.txt", 'w')
        wr.write("stopped")
        wr.close()

    def run_game(self):
        wr = open("app/db/state.txt", 'w')
        wr.write("running")
        wr.close()