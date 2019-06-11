"""
Class representing a chess board, has methods for moving pieces and converting between notations
"""

import re
moves = """1. d4 Nf6 2. d5 c6 3. c4 cxd5 4. Qc2 e6 5. c5 Na6 6. Nf3 Bxc5 7. e3 Qa5+ 8. Nfd2
O-O 9. Bd3 g5 10. O-O b5 11. Nb3 Qa4 12. Nc3 Qg4 13. Nxb5 Nb4 14. Qxc5 Nxd3 15.
Qc2 Nxc1 16. Rfxc1 Ba6 17. Nc7 Bb7 18. Nxa8 Bxa8 19. Nc5 Rc8 20. b4 Ne4 21. f3
Qf5 22. fxe4 dxe4 23. Qd2 a5 24. Qxd7 Rc6 25. Qd8+ Kg7 26. Qxa8 Rxc5 27. bxc5 g4
28. c6 Qe5 29. c7 Qxa1 30. Rxa1 1-0"""

# TODO: methods seem like a complete disaster organizationally, maybe improve that
class Board:
    # used to split moves in pgn notation
    move_regex = re.compile(r"[1-9][0-9]?[0-9]?\. ")
    # white is uppercase, black is lowercase in standard FEN notation
    starting_pos = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]

    # convert algebraic notation to list indices
    # going down
    ranks = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    # going across
    file = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    def __init__(self, board=None):
        if board is not None:
            self.board = board
        else:
            self.board = self.starting_pos

    # moves a single move on the board
    # TODO: deal with ambiguous cases that arise with pawn capture
    # TODO: implement something that checks if a piece can move to a square?
    # ^ if I decide thats how I want to deal with deciding which piece to move in the case
    # where two are possible
    def single_move(self, move, color):
        # assign color
        black = False
        if color == "b":
            black = True

        # check if capture move
        capture = False
        if "x" in move:
            capture = True
            move.replace("x", "")
        # check if castling move
        if move == "O-O":
            if black:
                self.board[0][7] = None
                self.board[0][6] = 'k'
                self.board[0][5] = 'r'
            else:
                self.board[7][7] = None
                self.board[7][6] = 'K'
                self.board[7][5] = 'R'
        elif move == "O-O-O":
            if black:
                self.board[0][0] = None
                self.board[0][1] = 'k'
                self.board[0][2] = 'r'
            else:
                self.board[7][0] = None
                self.board[7][1] = 'K'
                self.board[7][2] = 'R'
        # check if not a pawn move
        if move[0] in "RNBQK":
            if black:
                if not capture:
        else:
            if black:
                if not capture:
                    file = files[move[0]]
                    rank = ranks[move[1]]
                    for rank in self.board:
                        if rank[file] == "p":
                            rank[file] = None
                    self.board[rank][file] = "p"
            else:
                if not capture:
                    file = files[move[0]]
                    rank = ranks[move[1]]
                    for rank in self.board:
                        if rank[file] == "P":
                            rank[file] = None
                    self.board[rank][file] = "P"



    # moves the board along a list of moves from pgn format
    def multiple_moves(self, move_string):
        move_list = self.move_string_to_list(move_string)
        for move in move_list:
            moves = move.split()
            for turn in moves:
                # check if the move is actually just saying who won
                if turn.startswith("1") or turn.startswith("0") or turn.startswith("1/2"):
                    print(turn)
                else:
                    if moves.index(turn) == 0:
                        self.single_move(turn, "w")
                    else:
                        self.single_move(turn, 'b')


    # converts pgn format moves to a list
    def move_string_to_list(self, move_string):
        move_string = move_string.replace("\n", " ")
        move_list = self.move_regex.split(move_string)
        # regex issue band-aid
        if move_list[0] == '':
            move_list.pop(0)
        return move_list

    # convert algebraic move list of pgn to FEN for stockfish/general usage
    # relies on the board starting at the start position, aka create a new object
    # for each usage
    def to_fen(self, move_string):
        move_list = self.move_string_to_list(move_string)
        active = None
        half_move = 0
        full_move = 1
        # castling privileges
        wkc = True
        wqc = True
        bkc = True
        bqc = True


if __name__ == '__main__':
    b = Board()
    print(b.move_string_to_list(moves))
    b.multiple_moves(moves)