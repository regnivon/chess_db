"""
Class to organize SQLite queries in a dict
"""


class Query:

    def __init__(self):
        self.commands = dict()

        self.commands["create table"] = """CREATE TABLE Games(
                white TEXT,
                whiteElo NUMERIC,
                black TEXT,
                blackElo NUMERIC,
                event TEXT,
                site TEXT,
                date DATE,
                time TIME,
                round TEXT,
                variant TEXT,
                timeControl NUMERIC,
                result TEXT,
                termination TEXT,
                moves TEXT
            )"""

        self.commands["insert game"] = """INSERT INTO Games VALUES 
                (?, ? ,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

        self.commands["select game white player"] = """SELECT * FROM Games WHERE
                white = ? 
                """

        self.commands["select game black player"] = """SELECT * FROM Games WHERE
                black = ? 
                """

        self.commands["select game exists"] = """SELECT * FROM Games WHERE
                date = ? AND time = ?
        """

        self.commands["select game datetime"] = """SELECT white, whiteElo, black, blackElo
        ,date, time FROM Games
        """

