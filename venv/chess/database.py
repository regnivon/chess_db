import sqlite3
import os
from query import Query
import json


class Database:

    def __init__(self, settings, auto_connect=True, query=None):
        self.settings = settings["database"]
        self.path = self.settings["db_dir"]
        self.connected = False
        self.connection = None
        self.cursor = None
        self.user = None
        self.create = False
        
        # will initialize a query object if one is not passed, otherwise use the one passed
        # to avoid creating multiple during a run
        if query is None:
            self.query = Query()
        else:
            self.query = query

        if auto_connect:
            self.connect()

        # if database was created during the connect method this runs
        if self.create:
            print("Creating tables.")
            self.create_table()

    def connect(self):
        if not os.path.isdir(self.settings["db_dir"]):
            print("Initializing database.")
            os.mkdir("database")
            self.path = os.path.join(self.settings["db_dir"])
            self.create = True
        print("Connecting to database.")
        if os.path.exists(self.path):
            self.connection = sqlite3.connect(self.path + "/database.db")
            self.connected = True
        if self.is_connected():
            self.cursor = self.connection.cursor()

    def is_connected(self):
        return self.connected

    def close(self):
        self.connection.close()
        self.connected = False

    def commit(self):
        try:
            self.connection.commit()
        except error as e:
            print("Failed to commit")
            print(e)

    # check if a game already exists, checks date and time probably shouldn't fail ever
    # unless playing multiple games which somehow have simultaneous endings
    def already_exists(self, game):
        cur = self.cursor
        cur.execute(self.query.commands["select game exists"], (game.date, game.end_time))
        return len(cur.fetchall()) > 0

    # fetches all games in db with passed player on passed color
    def fetch_by_color(self, player, color):
        cur = self.cursor
        cur.execute(self.query.commands["select game {color} player".format(color=color)], (player,) )
        return cur.fetchall()

    def fetch(self):
        cur = self.cursor
        cur.execute("select * from Games")
        return cur.fetchall()

    def create_table(self):
        cursor = self.cursor
        cursor.execute(self.query.commands["create table"])

    def insert_game(self, game):
        self.cursor.execute(self.query.commands["insert game"], (
            game.white, game.w_elo, game.black, game.b_elo,
            game.event, game.site, game.date, game.end_time,
            game.round, game.variant, game.timecont,
            game.result, game.term, game.moves
        ))


if __name__ == '__main__':
    f = open("test/settings.json", 'r')
    load = json.load(f)
    print(load)

    d = Database(load)

    for item in x:
        print(item)

    s = open("test/settings.json", 'w')

    json.dump(load, s)


