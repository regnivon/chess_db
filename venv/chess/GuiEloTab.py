"""
Tab to graph Elo vs Time
"""

# PyQt5 modules
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QFrame, QPushButton
from PyQt5.QtGui import QIcon

# external libraries
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.font_manager import FontProperties


class EloGraph(QSplitter):

    def __init__(self, database, top):
        super().__init__()
        self.db = database

        frame = QFrame()
        self.graphBox = QVBoxLayout()
        frame.setLayout(self.graphBox)
        self.addWidget(frame)
        self.pushButton1 = QPushButton("PyQt5 button")
        self.addWidget(self.pushButton1)

    def graph(self):
        data = self.db.elo_by_date()






