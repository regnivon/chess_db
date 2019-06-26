"""
GUI class for analysis options prompt
"""

from PyQt5.QtCore import (QCoreApplication, QDate, Qt)
from PyQt5.QtGui import (QColor, QImage, QPainter, QIcon, QFont)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QWidget, QAction, QMenu, QDialog, QLabel, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QFormLayout, QGroupBox, QDialogButtonBox)


class AnalysisOptions(QDialog):

    def __init__(self, analysis):
        super().__init__()
        self.analysis = analysis

        # create the fields
        self.create_options()

        # create buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.frame)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.setWindowTitle("Analysis Options")

    def create_options(self):
        self.frame = QGroupBox("Options")
        layout = QFormLayout()
        self.eng_line = QLineEdit("stockfish/src/stockfish")
        self.tab_line = QLineEdit(str(self.analysis.num_games))
        self.thresh_line = QLineEdit(str(self.analysis.threshold))
        self.user_line = QLineEdit(self.analysis.user)
        layout.addRow(QLabel("Engine Path"), self.eng_line)
        layout.addRow(QLabel("Table Length"), self.tab_line)
        layout.addRow(QLabel("Analysis Threshold"), self.thresh_line)
        layout.addRow(QLabel("Username"), self.user_line)
        self.frame.setLayout(layout)

    def accept(self):
        # change analysis object settings and exit
        self.analysis.engine_path = self.eng_line.text()
        self.analysis.num_games = int(self.tab_line.text())
        self.analysis.threshold = int(self.thresh_line.text())
        self.analysis.user = self.user_line.text()
        self.analysis.update_options()
        self.close()


