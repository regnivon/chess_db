"""
Implements class to integrate the stockfish chess engine so that it can analyze
board positions and moves
"""

# builtins
import subprocess
import re
import copy

import database
import board


class Integration:

    best_move_regex = re.compile(r"[a-h][1-8][a-h][1-8]")

    def __init__(self, stockfish_path=None, depth=None):

        if stockfish_path is not None:
            self.stockfish_path=stockfish_path
        else:
            stockfish_path = "stockfish/src/stockfish"

        # default stockfish input, can change with user input
        if depth:
            self.depth = depth
        else:
            self.depth = 10
        self.stockfish = subprocess.Popen(stockfish_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

    def set_pos(self, position):
        self.stockfish.stdin.write("position fen " + position + "\n")

    def go(self):
        self.stockfish.stdin.write("go depth {depth} \n".format(depth=self.depth))
        for i in range(self.depth + 1):
            self.stockfish.stdout.readline()
        best_move = self.best_move_regex.search(self.stockfish.stdout.readline()).group(0)
        return best_move

    def set_depth(self, depth):
        self.depth = depth

    def close(self):
        self.stockfish.terminate()

    def eval(self):
        self.stockfish.stdin.write("eval \n")
        for i in range(19):
            self.stockfish.stdout.readline()
        score = self.stockfish.stdout.readline()
        return score.split()[2]

    def print_pos(self):
        self.stockfish.stdin.write("d \n")
        for i in range(22):
            print(f.stockfish.stdout.readline())


if __name__ == '__main__':
    moves = """1. d4 Nf6 2. d5 c6 3. c4 cxd5 4. Qc2 e6 5. c5 Na6 6. Nf3 Bxc5 7. e3 Qa5+ 8. Nfd2 O-O 9. Bd3 g5 10. O-O b5 
    11. Nb3 Qa4 12. Nc3 Qg4 13. Nxb5 Nb4 14. Qxc5 Nxd3 15.
Qc2 Nxc1 16. Rfxc1 Ba6 17. Nc7 Bb7 18. Nxa8 Bxa8 19. Nc5 Rc8 20. b4 Ne4 21. f3
Qf5 22. fxe4 dxe4 23. Qd2 a5 24. Qxd7 Rc6 25. Qd8+ Kg7 26. Qxa8 Rxc5 27. bxc5 g4
28. c6 Qe5 29. c7 Qxa1 30. Rxa1 1-0"""
    moves2 = """1. d4 Nf6"""
    settings = {"database": {"db_dir": "database"}, "user": "regnivon"}
    b = board.Board()
    f = Integration()
    f.set_depth(10)
    db = database.Database(settings)
    for game in db.fetch_all():
        move = game[13].split("200.")
        #print(move)
        #if "1. Nf3 Nc6 2. c4 Nf6 3. d4 d6 4. Bd2 Bg4 5. g3 Bxf3 6. exf3 g6 7. f4 Bg7 8. Bg2 Qc8 9. O-O Nxd4 10. Qa4+ Nd7" in move[0]:
        if "1. Nf3 Nc6 2. c4 Nf6 3. d4 d6 4. Bd2 Bg4 5. g3 Bxf3 6. exf3 g6" in move[0]:

            b.to_fen(move_string="1. Nf3 Nc6 2. c4 Nf6 3. d4")
            print(b)
            print(b.fen)
            f = copy.deepcopy(b)
            b.to_fen(move_string="d6 4. Bd2")
            print(b)
            print(b.fen)
            print(f)
            print(f.fen)
            b.reset()
            b.to_fen(move_string="1. Nf3 Nc6")
            b.to_fen(move_string="2. c4 Nf6 3. d4")
            #print(b)
            #print(b.fen)
            #print(move[0])
            #print(b)
            #print(b.fen)
            #f.set_pos(b.fen)
            #print(f.go())
            #print(f.eval())
            #b.reset()




