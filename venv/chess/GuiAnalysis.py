# builtins
from datetime import datetime

# PyQt5 imports
from PyQt5.QtCore import (QCoreApplication, QDate, Qt)
from PyQt5.QtWidgets import (QPushButton, QWidget, QDialog, QLabel, QVBoxLayout,
                             QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QInputDialog, QLineEdit, QSplitter, QHeaderView)

# program files
import integration
import board
import copy


class Analysis(QSplitter):

    def __init__(self, db, settings):
        super().__init__(Qt.Vertical)
        self.user = settings["user"]
        self.engine_path = settings["engine"]["path"]
        self.engine = integration.Integration(stockfish_path=self.engine_path)
        self.db = db
        self.board = board.Board()
        self.recent_games_table = None
        # default recent games to display
        self.num_games = 50
        self.games = None
        self.current_game_moves = None
        self.current_game_color = None

        # fetch recent games to create table
        self.fetch_games()

        self.btn_wid = None
        self.label_widget = None
        self.btns_and_labels = QWidget()
        self.btns_and_labels_layout = QHBoxLayout()
        self.btns_and_labels.setLayout(self.btns_and_labels_layout)

        self.create_buttons()
        self.create_labels()

        self.btns_and_labels_layout.addWidget(self.label_widget)
        self.btns_and_labels_layout.addWidget(self.btn_wid)
        self.addWidget(self.btns_and_labels)

        self.create_table()

    # resets the board then moves it along the given move string
    def input_moves(self, move_string):
        self.board.reset()
        self.board.to_fen(move_string)

    # move the board along a single move without resetting
    def input_single_move(self, move):
        self.board.to_fen(move)

    # input a single move in the full algebraic form without resetting board
    def input_single__full_move(self, move):
        self.board.full_single_move(move)

    def analyze_position(self, fen):
        self.engine.set_pos(fen)
        best_move = self.engine.go()
        cur_pos_eval = self.engine.eval()
        self.analysis_label.setText(f"Analysis: {best_move} {cur_pos_eval}")
        return best_move, cur_pos_eval

    def analyze_moves(self):
        move_string, ok = QInputDialog.getText(self, "Configuration", "Input moves:", QLineEdit.Normal)
        if ok:
            self.input_moves(move_string)
            self.analyze_position(self.board.fen)

    def create_table(self):
        self.recent_games_table = QTableWidget(self.num_games, 7)
        self.recent_games_table.setHorizontalHeaderLabels(["Date", "White", "White Elo", "Black", "Black Elo", "Result",
                                                           "Moves"])
        for i in range(6):
            self.recent_games_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        for i in range(0, self.num_games):
            info = self.games[i]
            self.recent_games_table.setItem(i, 0, QTableWidgetItem(info[0].strftime("%d-%m-%Y %H:%M:%S")))
            self.recent_games_table.setItem(i, 1, QTableWidgetItem(info[1]))
            self.recent_games_table.setItem(i, 2, QTableWidgetItem(str(info[2])))
            self.recent_games_table.setItem(i, 3, QTableWidgetItem(info[3]))
            self.recent_games_table.setItem(i, 4, QTableWidgetItem(str(info[4])))
            self.recent_games_table.setItem(i, 5, QTableWidgetItem(info[5]))
            self.recent_games_table.setItem(i, 6, QTableWidgetItem(info[6]))
        self.recent_games_table.doubleClicked.connect(self.double_click_game)

        self.addWidget(self.recent_games_table)

    def create_buttons(self):
        self.btn_wid = QWidget()
        self.btn_wid_layout = QHBoxLayout()
        self.btn_wid.setLayout(self.btn_wid_layout)

        input_button = QPushButton("Input Moves")
        input_button.clicked.connect(self.analyze_moves)
        num_games_button = QPushButton("Number of games displayed")
        num_games_button.clicked.connect(self.query_num)
        refresh_button = QPushButton("Refresh table")
        refresh_button.clicked.connect(self.refresh_table)

        self.btn_wid_layout.addWidget(input_button)
        self.btn_wid_layout.addWidget(num_games_button)
        self.btn_wid_layout.addWidget(refresh_button)

    def create_labels(self):
        self.label_widget = QWidget()
        self.label_layout = QVBoxLayout()
        self.label_widget.setLayout(self.label_layout)

        self.analysis_label = QLabel("Analysis: ")
        self.moves_label = QLabel("Moves: ")

        self.label_layout.addWidget(self.analysis_label)
        self.label_layout.addWidget(self.moves_label)

    def fetch_games(self):
        data = self.db.game_by_date()
        self.games = data
        if self.num_games > len(data):
            self.num_games = len(data)

    def double_click_game(self):
        self.board.reset()
        row = self.recent_games_table.currentRow()
        moves = self.recent_games_table.item(row, 6).text()
        f = moves.split(" ")
        formatted_moves = ""
        for item_count, item in enumerate(f):
            formatted_moves += f"{item} "
            if item_count % 11 == 0 and item_count > 0:
                formatted_moves += "\n"
        self.moves_label.setText(f"Moves: {formatted_moves}")
        self.current_game_moves = moves
        if self.user == self.recent_games_table.item(row, 1).text():
            self.current_game_color = "w"
        else:
            self.current_game_color = "b"
        self.analyze_game()

    def analyze_game(self):
        split_moves = self.board.move_regex.split(self.current_game_moves)
        split_moves.pop(0)
        print(split_moves)
        all_moves = list()
        for move in split_moves:
            move = move.split(" ")
            all_moves.append(move[0])
            all_moves.append(move[1])
        analysis_list = list()
        if self.current_game_color == "w":
            for num, move in enumerate(split_moves):
                analysis_list.append(f"{num+1}. {move}")
        else:
            analysis_list.append("1. " + all_moves.pop(0))
            move_count = 2
            while len(all_moves) >= 2:
                analysis_list.append(f"{all_moves[0]} {move_count}. {all_moves[1]}")
                all_moves.pop(0)
                all_moves.pop(0)
                move_count += 1
        print(analysis_list)
        for move in analysis_list:
            if "#" not in move:
                # for each decision point of the player, find the value of the board after they make their move
                # and then find the difference of that value with what stockfish would have done
                self.input_single_move(move)
                temp_board = self.board.duplicate()
                self.analyze_position(self.board.fen)

    def query_num(self):
        num, ok = QInputDialog.getInt(self, "Configuration", "Input moves:", QLineEdit.Normal)
        if ok:
            if len(self.games) > num:
                self.num_games = num
            else:
                self.num_games = len(self.games)
            self.recreate_table()

    def refresh_table(self):
        self.num_games = 50
        self.fetch_games()
        self.recreate_table()

    def recreate_table(self):
        self.recent_games_table.hide()
        self.recent_games_table.deleteLater()
        self.recent_games_table = None
        self.create_table()









