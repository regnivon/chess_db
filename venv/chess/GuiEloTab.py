"""
Tab to graph Elo vs Time
"""

import random
import datetime

# PyQt5 modules

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSplitter, QVBoxLayout, QFrame,
                             QPushButton, QWidget, QHBoxLayout, QLabel)


# external libraries
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.font_manager import FontProperties


class EloGraph(QSplitter):

    def __init__(self, database):
        super().__init__(Qt.Vertical)
        self.db = database
        self.canvas = None
        self.figure = None
        self.ax = None
        self.game = False
        self.elo_list = None
        self.date_list = None

        frame = QFrame()
        self.box = QHBoxLayout()
        frame.setLayout(self.box)
        self.addWidget(frame)

        game_btn = QPushButton("By Games")
        game_btn.setGeometry(200, 10, 50, 50)
        game_btn.clicked.connect(self.graph_by_game)
        date_btn = QPushButton("By Date")
        date_btn.clicked.connect(self.graph_by_date)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_graph)

        self.btn_splitter = QSplitter(Qt.Vertical)
        self.btn_splitter.setFrameShape(QFrame.StyledPanel)

        self.btn_splitter.addWidget(game_btn)
        self.btn_splitter.addWidget(date_btn)
        self.btn_splitter.addWidget(refresh_btn)
        self.addWidget(self.btn_splitter)



        self.fetch_games()
        self.graph_by_date()

    def graph_by_date(self):
        self.game = False
        self.clear_graph()
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(self.date_list, self.elo_list)
        self.ax.set_title('ELO by Date')
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Elo")
        self.box.addWidget(self.canvas)
        self.canvas.draw()

    def graph_by_game(self):
        self.game = True
        self.clear_graph()
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(self.elo_list)
        self.ax.set_title('ELO by Game')
        self.ax.set_xlabel("Games")
        self.ax.set_ylabel("Elo")
        self.box.addWidget(self.canvas)
        self.canvas.draw()

    def clear_graph(self):
        if self.canvas is not None:
            self.box.removeWidget(self.canvas)

        if self.figure is not None:
            self.figure.clear()

        if self.ax is not None:
            self.ax.clear()

        self.figure = Figure(figsize=(10.0, 6.0), dpi=80)
        self.canvas = FigureCanvas(self.figure)

    def refresh_graph(self):
        self.fetch_games()
        if self.game:
            self.graph_by_game()
        else:
            self.graph_by_date()

    def fetch_games(self):
        data = self.db.elo_by_date()
        self.elo_list = list()
        self.date_list = list()
        for game in data:
            self.elo_list.append(game[0])
            self.date_list.append(game[1])





