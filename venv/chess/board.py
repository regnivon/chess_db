"""
Class representing a chess board, has methods for moving pieces and converting between notations
"""

import re
import copy
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
    files = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    def __init__(self, ):

        self.board = copy.deepcopy(self.starting_pos)
        # game state tracking for FEN conversion
        self.fen = None
        self.active = "w"
        self.half_move = 0
        self.full_move = 1
        # castling privileges
        self.wkc = True
        self.wqc = True
        self.bkc = True
        self.bqc = True
        # en passant target
        self.ep = "-"
        # keeps track of if a check move was played
        self.check = False

    # TODO: This method in general is a complete disaster
    # I think this method more or less works and has mostly every scenario,
    # except maybe ambiguious promotions?
    # but it is massive, needs to be broken down if possible.
    # moves a single move on the board
    def single_move(self, move, color, check):
        # assign color
        black = False
        if color == "b":
            black = True
        # check if capture move
        capture = False
        if "x" in move:
            capture = True
            move = move.replace("x", "")
        # remove check and mate symbols
        if "+" in move:
            move = move.replace("+", "")
        if "#" in move:
            move = move.replace("#", "")
        # check if castling move
        if move == "O-O":
            if black:
                self.board[0][7] = None
                self.board[0][6] = 'k'
                self.board[0][5] = 'r'
                self.board[0][4] = None
            else:
                self.board[7][7] = None
                self.board[7][6] = 'K'
                self.board[7][5] = 'R'
                self.board[7][4] = None
        elif move == "O-O-O":
            if black:
                self.board[0][0] = None
                self.board[0][2] = 'k'
                self.board[0][3] = 'r'
                self.board[0][4] = None
            else:
                self.board[7][0] = None
                self.board[7][2] = 'K'
                self.board[7][3] = 'R'
                self.board[7][4] = None
        # check if queen or king move, which can just be carried out
        elif move[0] == "K":
            rank = self.ranks[move[2]]
            file = self.files[move[1]]
            if black:
                for row in self.board:
                    for sq in row:
                        if sq == "k":
                            row[row.index(sq)] = None
                self.board[rank][file] = "k"
            else:
                for row in self.board:
                    for sq in row:
                        if sq == "K":
                            row[row.index(sq)] = None
                self.board[rank][file] = "K"
        elif move[0] == "Q":
            rank = self.ranks[move[2]]
            file = self.files[move[1]]
            if black:
                for row in self.board:
                    for sq in row:
                        if sq == "q":
                            row[row.index(sq)] = None
                self.board[rank][file] = "q"
            else:
                for row in self.board:
                    for sq in row:
                        if sq == "Q":
                            row[row.index(sq)] = None
                self.board[rank][file] = "Q"
        # check if piece has a pair piece, which leads to ambiguities
        elif move[0] in "RNB":
            # since strings were prestripped of things like + and x, can check if ambiguous move
            # or not by length ie Rfd2 vs Rd2
            piece = move[0]
            ambiguous = False
            if black:
                piece = piece.lower()
            if len(move) == 3:
                ambiguous = True
            if ambiguous:
                # ambiguous so we need to check which piece can actually move to that square
                # TODO: track pieces being removed and maybe simplify this check if only one
                # still exists
                rank = self.ranks[move[2]]
                file = self.files[move[1]]
                for row_num, row in enumerate(self.board):
                    for col_num, sq in enumerate(row):
                        if sq == piece:
                            if self.can_move(piece, row_num, col_num, rank, file, check):
                                self.board[row_num][col_num] = None
                                self.board[rank][file] = piece
                                return
            else:
                # these variables are held in terms of list indices
                # find where the piece is
                rank = None
                file = None
                to_rank = None
                to_file = None
                if len(move) == 4:
                    if move[1] in self.ranks.keys():
                        rank = self.ranks[move[1]]
                    else:
                        file = self.files[move[1]]
                    to_rank = self.ranks[move[3]]
                    to_file = self.files[move[2]]
                elif len(move) == 5:
                    rank = self.ranks[move[1]]
                    file = self.files[move[2]]
                    to_rank = self.ranks[move[4]]
                    to_file = self.files[move[3]]
                if not rank:
                    rank = self.find_piece(piece, file=file)
                elif not file:
                    file = self.find_piece(piece, rank=rank)
                self.board[rank][file] = None
                self.board[to_rank][to_file] = piece
        elif "=" in move:
            promo_file = self.files[move[move.index("=")-2]]
            promo_rank = self.ranks[move[move.index("=")-1]]
            promo_piece = move[-1]
            if promo_rank == 0:
                self.board[promo_rank + 1][promo_file] = None
                self.board[promo_rank][promo_file] = promo_piece
            # black promo
            else:
                self.board[promo_rank-1][promo_file] = None
                self.board[promo_rank][promo_file] = promo_piece.lower()
        else:
            if black:
                # no ambiguities with non-capture moves
                if not capture:
                    file = self.files[move[0]]
                    rank = self.ranks[move[1]]
                    for row_num, row in enumerate(self.board):
                        if row[file] == "p" and (rank == row_num + 1 or rank == row_num + 2):
                            # extra check for pawns that are stacked on a file
                            if rank == row_num + 2 and self.board[row_num + 1][file] is None:
                                row[file] = None
                            elif rank == row_num + 1:
                                row[file] = None
                    self.board[rank][file] = "p"
                else:
                    file = self.files[move[0]]
                    to_rank = self.ranks[move[2]]
                    to_file = self.files[move[1]]
                    for row_num, row in enumerate(self.board):
                        if row[file] == "p" and to_rank == row_num + 1:
                            row[file] = None
                            # check if capturing en passant
                            if self.board[to_rank][to_file] is None:
                                self.board[to_rank - 1][to_file] = None
                            self.board[to_rank][to_file] = "p"
            else:
                if not capture:
                    file = self.files[move[0]]
                    rank = self.ranks[move[1]]
                    for row_num, row in enumerate(self.board):
                        if row[file] == "P" and (rank == row_num - 1 or rank == row_num - 2):
                            row[file] = None
                    self.board[rank][file] = "P"
                else:
                    file = self.files[move[0]]
                    to_rank = self.ranks[move[2]]
                    to_file = self.files[move[1]]
                    for row_num, row in enumerate(self.board):
                        if row[file] == "P" and to_rank == row_num - 1:
                            row[file] = None
                            # check if capturing en passant
                            if self.board[to_rank][to_file] is None:
                                self.board[to_rank + 1][to_file] = None
                            self.board[to_rank][to_file] = "P"

    # moves the board along a list of moves from pgn format, this might be useless
    # since FEN state might always want to be held, and in that case the to_fen method should
    # do all the moving not sure tho
    def multiple_moves(self, move_string):
        move_list = self.move_string_to_list(move_string)
        for move in move_list:
            moves = move.split()
            for turn in moves:
                # check if the move is actually just saying who won
                if turn.startswith("1") or turn.startswith("0") or turn.startswith("1/2"):
                    print(turn)
                    print(self)
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

    """ 
    convert algebraic move list of pgn to FEN for stockfish/general usage
    relies on the board starting at the start position, aka create a new object
    for each usage. call the single move method multiple times like multiple_moves,
    but also check for the things that need to be output in FEN
    If this method is not passed a string of moves, it will instead just 
    set the FEN variable of the board object 
    """
    def to_fen(self, move_string=None):
        split_moves = list()
        if move_string:
            move_list = self.move_string_to_list(move_string)
            for move in move_list:
                move = move.split()
                split_moves.append(move[0])
                if len(move) > 1:
                    split_moves.append(move[1])
            for move in split_moves:
                if not (move.startswith("1") or move.startswith("0") or move.startswith("1/2")):
                    # reset en passant target
                    if not self.ep == "-":
                        self.ep = "-"
                    if "O-O" in move:
                        if self.active == "w":
                            self.wkc = False
                            self.wqc = False
                        else:
                            self.bkc = False
                            self.bqc = False
                    elif "O-O-O" in move:
                        if self.active == "w":
                            self.wkc = False
                            self.wqc = False
                        else:
                            self.bkc = False
                            self.bqc = False
                    elif move[0] not in "RNBKQ" and "x" not in move:
                        self.half_move = 0
                        # check if this move leads to en passant availability
                        file = self.files[move[0]]
                        rank = self.ranks[move[1]]
                        if self.active == "w":
                            if self.board[rank + 2][file] == "P" and not self.board[rank + 1][file] == "P":
                                self.ep = move[0] + str(int(move[1]) - 1)
                        else:
                            if self.board[rank - 2][file] == "p" and not self.board[rank - 1][file] == "p":
                                self.ep = move[0] + str(int(move[1]) + 1)
                    else:
                        self.half_move += 1
                    # remove castling rights after king move
                    if move[0] == "K":
                        if self.active == "w":
                            self.wkc = False
                            self.wqc = False
                        else:
                            self.bkc = False
                            self.bqc = False
                    self.single_move(move, self.active, self.check)
                    if self.check:
                        self.check = False
                    if "+" in move:
                        self.check = True
                    #print(move)
                    #print(self)
                    # check which castling rights are gone
                    if move[0] == "R":
                        if self.active == "w":
                            if not self.board[7][0] == "R" and self.wqc:
                                self.wqc = False
                            elif not self.board[7][7] == "R" and self.wkc:
                                self.wkc = False
                        else:
                            if not self.board[0][0] == "r" and self.bqc:
                                self.bqc = False
                            elif not self.board[0][7] == "r" and self.bkc:
                                self.bkc = False
                    if self.active == "w":
                        self.active = "b"
                    else:
                        self.active = "w"
                        self.full_move += 1
        fen_string = ""
        # add position to string
        for row_num, row in enumerate(self.board):
            blank_count = 0
            for sq in row:
                if sq is not None:
                    if blank_count > 0:
                        fen_string += str(blank_count)
                        fen_string += sq
                        blank_count = 0
                    else:
                        fen_string += sq
                else:
                    blank_count += 1
            if row_num < 7:
                if blank_count > 0:
                    fen_string += str(blank_count)
                fen_string += "/"
            elif row_num == 7:
                if blank_count > 0:
                    fen_string += str(blank_count)
        w_k = ""
        w_q = ""
        b_k = ""
        b_q = ""
        if not (self.wkc or self.wqc or self.bkc or self.bqc):
            w_k = "-"
        if self.wkc:
            w_k = "K"
        if self.wqc:
            w_q = "Q"
        if self.bkc:
            b_k = "k"
        if self.bqc:
            b_q = "q"
        self.fen = f"{fen_string} {self.active} {w_k}{w_q}{b_k}{b_q} {self.ep} {self.half_move} {self.full_move}"

    # moves a single move in full algebraic notation, i.e. the output from stockfish
    # and adjusts the board object FEN variables
    def full_single_move(self, move):
        from_file = self.files[move[0]]
        from_rank = self.ranks[move[1]]
        to_file = self.files[move[2]]
        to_rank = self.ranks[move[3]]
        piece = self.board[from_rank][from_file]
        self.board[from_rank][from_file] = None
        if self.board[to_rank][to_file] is not None:
            self.half_move = 0
        else:
            self.half_move += 1
        self.board[to_rank][to_file] = piece
        if piece == "R":
            if not self.board[7][0] == "R" and self.wqc:
                self.wqc = False
            elif not self.board[7][7] == "R" and self.wkc:
                self.wkc = False
        elif piece == "r":
            if not self.board[0][0] == "r" and self.bqc:
                self.bqc = False
            elif not self.board[0][7] == "r" and self.bkc:
                self.bkc = False
        elif piece == "K" and self.wqc or self.wkc:
            self.wqc = False
            self.wkc = False
        elif piece == "k" and self.bqc or self.bkc:
            self.bqc = False
            self.bkc = False
        elif piece.upper() == "P":
            self.half_move = 0
            if abs(from_rank - to_rank) == 2:
                file = move[0]
                if self.active == "w":
                    rank = int(move[1]) + 1
                    self.ep = f"{file}{rank}"
                else:
                    rank = int(move[1]) - 1
                    self.ep = f"{file}{rank}"
        if self.active == "w":
            self.active = "b"
        else:
            self.active = "w"
            self.full_move += 1

    """
    checks if the passed piece can move to the given square
    pass rank and file information in terms of where to access on the list
    assumes that you are not giving it a move that is landing on a square
    with a piece you own and that you are not going off the board
    """
    def can_move(self, piece, from_rank, from_file, to_rank, to_file, check):
        # does not need to check if pieces in the way since bishops are distinct for their square color
        # so no ambiguity there
        if piece.upper() == "B":
            if not abs(from_rank - to_rank) == abs(from_file - to_file):
                return False
            self.board[from_rank][from_file] = None
            if not self.king_safe(self.active) and not check:
                self.board[from_rank][from_file] = piece
                return False
            if check:
                cur_piece = self.board[to_rank][to_file]
                self.board[to_rank][to_file] = piece
                if not self.king_safe(self.active):
                    self.board[to_rank][to_file] = None
                    return False
                self.board[to_rank][to_file] = cur_piece
            self.board[from_rank][from_file] = piece
            return True
        if piece.upper() == "N":
            to_coord = [to_rank, to_file]
            possible_moves = [
                [from_rank+1, from_file+2],
                [from_rank+1, from_file-2],
                [from_rank-1, from_file+2],
                [from_rank-1, from_file-2],
                [from_rank+2, from_file+1],
                [from_rank+2, from_file-1],
                [from_rank-2, from_file+1],
                [from_rank-2, from_file-1]
            ]
            if to_coord not in possible_moves:
                return False
            self.board[from_rank][from_file] = None
            if not self.king_safe(self.active) and not check:
                self.board[from_rank][from_file] = piece
                return False
            if check:
                cur_piece = self.board[to_rank][to_file]
                self.board[to_rank][to_file] = piece
                if not self.king_safe(self.active):
                    self.board[to_rank][to_file] = None
                    return False
                self.board[to_rank][to_file] = cur_piece
            self.board[from_rank][from_file] = piece
            return True
        if piece.upper() == "R":
            # check if follows general rook movement rules, then check if
            # any pieces in the way to remove the extra ambiguity
            if from_rank == to_rank or from_file == to_file:
                if from_rank != to_rank:
                    if from_rank > to_rank:
                        for intermediate_rank in range(to_rank + 1, from_rank):
                            if self.board[intermediate_rank][from_file] is not None:
                                return False
                    else:
                        for intermediate_rank in range(from_rank + 1, to_rank):
                            if self.board[intermediate_rank][from_file] is not None:
                                return False
                else:
                    if from_file > to_file:
                        for intermediate_file in range(to_file + 1, from_file):
                            if self.board[from_rank][intermediate_file] is not None:
                                return False
                    else:
                        for intermediate_file in range(from_file + 1, to_file):
                            if self.board[from_rank][intermediate_file] is not None:
                                return False
                self.board[from_rank][from_file] = None
                if not self.king_safe(self.active) and not check:
                    self.board[from_rank][from_file] = piece
                    return False
                if check:
                    cur_piece = self.board[to_rank][to_file]
                    self.board[to_rank][to_file] = piece
                    if not self.king_safe(self.active):
                        self.board[to_rank][to_file] = None
                        return False
                    self.board[to_rank][to_file] = cur_piece
                self.board[from_rank][from_file] = piece

                return True
            else:
                return False

    # this method is mainly used for checking if a piece can be moved, apparently if two pieces can both move to
    # a certain square, but one of them cannot be moved because that would allow your opponent to capture your king
    # then that is considered an unambiguous move in algebraic notation, so this checks if the king can be
    # captured from any diagonal or straight line
    def king_safe(self, color):
        piece = "K"
        king_rank = None
        king_file = None
        if color == "b":
            piece = "k"
        for row_num, row in enumerate(self.board):
            for col_num, sq in enumerate(row):
                if sq == piece:
                    king_rank = row_num
                    king_file = col_num
        # booleans for safety from a certain direction
        left_row = None
        right_row = None
        up_col = None
        down_col = None
        up_l_dia = None
        up_r_dia = None
        down_l_dia = None
        down_r_dia = None

        # check row and column safety, basically just check if the first piece encountered
        # is either ours or able to attack the king
        for sq in reversed(range(king_file)):
            if left_row is None:
                if color == "b":
                    if self.board[king_rank][sq] is not None:
                        if self.board[king_rank][sq].islower():
                            left_row = True
                        elif self.board[king_rank][sq] == "Q" or self.board[king_rank][sq] == "R":
                            left_row = False
                        else:
                            left_row = True
                if color == "w":
                    if self.board[king_rank][sq] is not None:
                        if self.board[king_rank][sq].isupper():
                            left_row = True
                        elif self.board[king_rank][sq] == "q" or self.board[king_rank][sq] == "r":
                            left_row = False
                        else:
                            left_row = True
        if left_row is None:
            left_row = True
        for sq in range(king_file + 1, 8):
            if right_row is None:
                if color == "b":
                    if self.board[king_rank][sq] is not None:
                        if self.board[king_rank][sq].islower():
                            right_row = True
                        elif self.board[king_rank][sq] == "Q" or self.board[king_rank][sq] == "R":
                            right_row = False
                        else:
                            right_row = True
                else:
                    if self.board[king_rank][sq] is not None:
                        if self.board[king_rank][sq].isupper():
                            right_row = True
                        elif self.board[king_rank][sq] == "q" or self.board[king_rank][sq] == "r":
                            right_row = False
                        else:
                            right_row = True
        if right_row is None:
            right_row = True
        for sq in reversed(range(king_rank)):
            if up_col is None:
                if color == "b":
                    if self.board[sq][king_file] is not None:
                        if self.board[sq][king_file].islower():
                            up_col = True
                        elif self.board[sq][king_file] == "Q" or self.board[sq][king_file] == "R":
                            up_col = False
                        else:
                            up_col = True
                else:
                    if self.board[sq][king_file] is not None:
                        if self.board[sq][king_file].isupper():
                            up_col = True
                        elif self.board[sq][king_file] == "q" or self.board[sq][king_file] == "r":
                            up_col = False
                        else:
                            up_col = True
        if up_col is None:
            up_col = True

        for sq in range(king_rank + 1, 8):
            if down_col is None:
                if color == "b":
                    if self.board[sq][king_file] is not None:
                        if self.board[sq][king_file].islower():
                            down_col = True
                        elif self.board[sq][king_file] == "Q" or self.board[sq][king_file] == "R":
                            down_col = False
                        else:
                            down_col = True
                else:
                    if self.board[sq][king_file] is not None:
                        if self.board[sq][king_file].isupper():
                            down_col = True
                        elif self.board[sq][king_file] == "q" or self.board[sq][king_file] == "r":
                            down_col = False
                        else:
                            down_col = True
        if down_col is None:
            down_col = True

        ul = zip(reversed(range(0, king_rank)), reversed(range(0, king_file)))
        ur = zip(reversed(range(0, king_rank)), range(king_file + 1, 8))
        dl = zip(range(king_rank + 1, 8), reversed(range(0, king_file)))
        dr = zip(range(king_rank + 1, 8), range(king_file + 1, 8))
        for sq in ul:
            if up_l_dia is None:
                if color == "b":
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].islower():
                            up_l_dia = True
                        elif self.board[sq[0]][sq[1]] == "Q" or self.board[sq[0]][sq[1]] == "B":
                            up_l_dia = False
                        else:
                            up_l_dia = True
                else:
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].isupper():
                            up_l_dia = True
                        elif self.board[sq[0]][sq[1]] == "q" or self.board[sq[0]][sq[1]] == "b":
                            up_l_dia = False
                        else:
                            up_l_dia = True
        if up_l_dia is None:
            up_l_dia = True
        for sq in ur:
            if up_r_dia is None:
                if color == "b":
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].islower():
                            up_r_dia = True
                        elif self.board[sq[0]][sq[1]] == "Q" or self.board[sq[0]][sq[1]] == "B":
                            up_r_dia = False
                        else:
                            up_r_dia = True
                else:
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].isupper():
                            up_r_dia = True
                        elif self.board[sq[0]][sq[1]] == "q" or self.board[sq[0]][sq[1]] == "b":
                            up_r_dia = False
                        else:
                            up_r_dia = True
        if up_r_dia is None:
            up_r_dia = True
        for sq in dl:
            if down_l_dia is None:
                if color == "b":
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].islower():
                            down_l_dia = True
                        elif self.board[sq[0]][sq[1]] == "Q" or self.board[sq[0]][sq[1]] == "B":
                            down_l_dia = False
                        else:
                            down_l_dia = True
                else:
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].isupper():
                            down_l_dia = True
                        elif self.board[sq[0]][sq[1]] == "q" or self.board[sq[0]][sq[1]] == "b":
                            down_l_dia = False
                        else:
                            down_l_dia = True
        if down_l_dia is None:
            down_l_dia = True
        for sq in dr:
            if down_r_dia is None:
                if color == "b":
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].islower():
                            down_r_dia = True
                        elif self.board[sq[0]][sq[1]] == "Q" or self.board[sq[0]][sq[1]] == "B":
                            down_r_dia = False
                        else:
                            down_r_dia = True
                else:
                    if self.board[sq[0]][sq[1]] is not None:
                        if self.board[sq[0]][sq[1]].isupper():
                            down_r_dia = True
                        elif self.board[sq[0]][sq[1]] == "q" or self.board[sq[0]][sq[1]] == "b":
                            down_r_dia = False
                        else:
                            down_r_dia = True
        if down_r_dia is None:
            down_r_dia = True
        #print(f"{left_row} {right_row} {up_col} {down_col} {up_l_dia} {up_r_dia} {down_l_dia} {down_r_dia}")
        if not (left_row and right_row and up_col and down_col and up_l_dia and up_r_dia and down_l_dia and down_r_dia):
            return False
        return True

    def find_piece(self, piece, file=None, rank=None):
        if rank is not None:
            rank_of_interest = self.board[rank]
            for sq in rank_of_interest:
                if sq == piece:
                    return rank_of_interest.index(sq)
        elif file is not None:
            for row in self.board:
                if row[file] == piece:
                    return self.board.index(row)

    def reset(self):
        self.board = copy.deepcopy(self.starting_pos)
        self.fen = None
        self.active = "w"
        self.half_move = 0
        self.full_move = 1
        self.wkc = True
        self.wqc = True
        self.bkc = True
        self.bqc = True
        self.ep = "-"

    #return depp copy of the board
    def duplicate(self):
        return copy.deepcopy(self)

    def __str__(self):
        to_return = ""
        for row in self.board:
            to_return += str(row) + "\n"
        return to_return


if __name__ == '__main__':
    b = Board()
    #print(b.move_string_to_list(moves))
    #b.multiple_moves(moves)
    print(b.to_fen(moves))
    print(b)
