"""
Implements class to integrate the stockfish chess engine so that it can analyze
board positions and moves
"""

# builtins
import subprocess


class Integration:

    def __init__(self, stockfish_path="stockfish/src/stockfish"):
        # default stockfish input, can change with user input
        self.depth = 10
        self.stockfish = subprocess.Popen(stockfish_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

    def pos(self, position):
        self.stockfish.stdin.write("position fen " + position + "\n")

    def go(self):
        self.stockfish.stdin.write("go depth {depth} \n".format(depth=self.depth))
        for i in range(self.depth + 2):
            print(self.stockfish.stdout.readline())

    def set_depth(self, depth):
        self.depth = depth

    def close(self):
        self.stockfish.terminate()

    def eval(self):
        self.stockfish.stdin.write("eval \n")
        for i in range(19):
            print(self.stockfish.stdout.readline())
        score = self.stockfish.stdout.readline()
        print(score.split())


if __name__ == '__main__':
    f = Integration()
    #f.set_depth(11)
    f.pos()
    f.go()
    f.eval()
    to_fen()
