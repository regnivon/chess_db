"""
reads pgn file format games and creates game objects which will write to database
"""
# builtins
import re
import json

# program files
import game
import database

# TODO: add a method call to write the game to the database


class Pgn:

    # regexes used to pull info out of header string, not entirely sure header
    # strings are consistent across sites but this is
    # what is in chess.com files
    fields_regex  = re.compile(r'".+?"')
    event_regex   = re.compile(r'Event ".+?"')
    site_regex    = re.compile(r'Site ".+?"')
    date_regex    = re.compile(r'Date ".+?"')
    round_regex   = re.compile(r'Round ".+?"')
    white_regex   = re.compile(r'White ".+?"')
    black_regex   = re.compile(r'Black ".+?"')
    result_regex  = re.compile(r'Result ".+?"')
    variant_regex = re.compile(r'variant ".+?"')
    w_elo_regex   = re.compile(r'WhiteElo ".+?"')
    b_elo_regex   = re.compile(r'BlackElo ".+?"')
    time_regex    = re.compile(r'TimeControl ".+?"')
    end_regex     = re.compile(r'EndTime ".+?"')
    term_regex    = re.compile(r'Termination ".+?"')

    # pass path to pgn file, pass settings dict
    def __init__(self, settings, database):
        self.settings = settings
        print(settings)
        self.player = settings["user"]
        # self.file   = filepath
        self.database = database

    # need to check this on large files might blow up if you have like years worth of
    # games in a file, this works on chess.com pgn files not sure about
    # any other site, pretty reliant on the formatting
    def read_pgn(self, file):
        data = self.database
        try:
            f = open(file, 'r')
            text = f.read()
            f.close()
            split_games = text.split("\n\n")
            num_games = int(len(split_games)/2)
            duplicates = 0
            imports = 0
            for i in range(0, num_games):
                g = game.Game()
                header_pos = i * 2
                self.read_game(split_games[header_pos], split_games[header_pos + 1], g)
                if not data.already_exists(g):
                    data.insert_game(g)
                    imports += 1
                else:
                    duplicates += 1
            data.commit()
            print("Imported {imp} games. There were {dup} duplicate games.".format(imp=imports, dup=duplicates))
        except Exception as e:
            print(e)

    # calls methods to get game info and adds to game object passed
    # each method finds what it is looking for with the appropriate
    # static regex and then scrubs the string
    def read_game(self, header, moves, game):
        self.read_site_event(header, game)
        self.read_date_round(header, game)
        self.read_player_data(header, game)
        self.read_result_data(header, game)
        self.read_game_data(header, game)
        self.read_moves(moves, game)

    # reads the site and event fields from the header
    def read_site_event(self, header, game):
        event = self.event_regex.search(header)
        if event:
            event = self.fields_regex.search(event.group(0))
            game.event = event.group(0).replace('"', '')
        site = self.site_regex.search(header)
        if site:
            site = self.fields_regex.search(site.group(0))
            game.site = site.group(0).replace('"', '')

    # reads the date and round fields
    def read_date_round(self, header, game):
        date = self.date_regex.search(header)
        if date:
            date = self.fields_regex.search(date.group(0))
            date = date.group(0).replace('"', '')
            date = date.replace(".", '-')
            game.date = date
        round = self.round_regex.search(header)
        if round:
            round = self.fields_regex.search(round.group(0))
            round = round.group(0).replace('"', '')
            game.round = round

    # reads ELO and player fields for each color
    def read_player_data(self, header, game):
        w_player = self.white_regex.search(header)
        if w_player:
            w_player = self.fields_regex.search(w_player.group(0))
            w_player = w_player.group(0).replace('"', '')
            game.white = w_player
        w_elo = self.w_elo_regex.search(header)
        if w_elo:
            w_elo = self.fields_regex.search(w_elo.group(0))
            w_elo = w_elo.group(0).replace('"', '')
            game.w_elo = int(w_elo)
        b_player = self.black_regex.search(header)
        if b_player:
            b_player = self.fields_regex.search(b_player.group(0))
            b_player = b_player.group(0).replace('"', '')
            game.black = b_player
        b_elo = self.b_elo_regex.search(header)
        if b_elo:
            b_elo = self.fields_regex.search(b_elo.group(0))
            b_elo = b_elo.group(0).replace('"', '')
            game.b_elo = int(b_elo)

    # reads fields having to do with the game ending
    def read_result_data(self, header, game):
        result = self.result_regex.search(header)
        if result:
            result = self.fields_regex.search(result.group(0))
            result = result.group(0).replace('"', '')
            game.result = result
        end_time = self.end_regex.search(header)
        if end_time:
            end_time = self.fields_regex.search(end_time.group(0))
            end_time = end_time.group(0).replace('"', '')
            game.end_time = end_time
        termination = self.term_regex.search(header)
        if termination:
            termination = self.fields_regex.search(termination.group(0))
            termination = termination.group(0).replace('"', '')
            game.term = termination

    # reads match specific data
    def read_game_data(self, header, game):
        variant = self.variant_regex.search(header)
        if variant:
            variant = self.fields_regex.search(variant.group(0))
            variant = variant.group(0).replace('"', '')
            game.variant = variant
        time_cont = self.time_regex.search(header)
        if time_cont:
            time_cont = self.fields_regex.search(time_cont.group(0))
            time_cont = time_cont.group(0).replace('"', '')
            game.timecont = int(time_cont)

    # reads moves
    def read_moves(self, moves, game):
        moves = moves.replace("\n", " ")
        moves = moves[0:len(moves)-4]
        game.moves = moves

        
if __name__ == '__main__':
    file = open("/Users/quentin/PycharmProjects/chess_db/venv/chess/items/settings.json")
    load = json.load(file)
    d = database.Database(load)
    pgn = Pgn(load, d)
    pgn.read_pgn("/Users/quentin/PycharmProjects/chess_db/venv/chess/test/chess_com_games_2019-04-15.pgn")











