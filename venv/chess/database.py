# builtins
import sqlite3
import os
import query
import json
import datetime

# program files
import query


class Database:

    def __init__(self, settings, auto_connect=True, default_query=None):
        self.user = settings["user"]
        self.settings = settings["database"]
        self.path = self.settings["db_dir"]
        self.connected = False
        self.connection = None
        self.cursor = None
        self.create = False
        
        # will initialize a query object if one is not passed, otherwise use the one passed
        # to avoid creating multiple during a run
        if default_query is None:
            self.query = query.Query()
        else:
            self.query = default_query
            
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

    def fetch_all(self):
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

    # fetches players, elos, and date time from all games
    # used for elo by time graph
    def elo_by_date(self):
        cur = self.cursor
        cur.execute(self.query.commands["select game datetime"])
        game_list = list()
        for game in cur.fetchall():
            to_add = list()
            if game[0] == self.user:
                to_add.append(game[1])
                date = game[4].split("-")
                time = game[5][0:8]
                time = time.split(":")
                d = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]),
                                      hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
                to_add.append(d)
                game_list.append(to_add)
            elif game[2] == self.user:
                to_add.append(game[3])
                date = game[4].split("-")
                time = game[5][0:8]
                time = time.split(":")
                d = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]),
                                      hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
                to_add.append(d)
                game_list.append(to_add)
        game_list = sorted(game_list, key=lambda x: x[1])
        return game_list

    def game_by_date(self):
        cur = self.cursor
        cur.execute(self.query.commands["select game table"])
        game_list = list()
        for game in cur.fetchall():
            to_add = list()
            date = game[4].split("-")
            time = game[5][0:8]
            time = time.split(":")
            d = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]),
                                  hour=int(time[0]), minute=int(time[1]), second=int(time[2]))
            to_add.append(d)
            to_add.append(game[0])
            to_add.append(game[1])
            to_add.append(game[2])
            to_add.append(game[3])
            to_add.append(game[6])
            to_add.append(game[7])
            game_list.append(to_add)
        game_list = sorted(game_list, key=lambda x: x[0], reverse=True)
        return game_list


if __name__ == '__main__':
    f = open("items/settings.json", 'r')
    load = json.load(f)
    print(load)

    q = query.Query()
    d = Database(load, query=q)

    d.elo_by_date()

    s = open("items/settings.json", 'w')

    json.dump(load, s)


