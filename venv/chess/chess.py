"""
Main program, will contain main GUI window and will execute functionality
"""
# built-ins
import re
import sys
import os


# PyQt5 imports
from PyQt5.QtCore import (QCoreApplication, QDate, Qt)
from PyQt5.QtGui import (QColor, QImage, QPainter, QIcon, QFont)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QWidget, QToolTip, QMessageBox, QTabWidget, QAction, QMenu, qApp,
                             QDialog, QLabel, QVBoxLayout, QDialogButtonBox, QFileDialog,
                             QInputDialog, QLineEdit)

# Chess program files
import config
import database
import query
import pgn

# GUI widgets
import GuiEloTab


class Chess(QMainWindow):

    def __init__(self):
        super().__init__()
        # None for now, created in load params class method
        # held here for the life of the program
        self.config = None
        self.query = None
        self.db = None
        self.user = None

        initial_x = 800
        initial_y = 600

        self.resize(initial_x, initial_y)

        # create initial tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "Main")
        self.tabs.addTab(self.tab2, "ELO")
        # create the menu bar
        self.create_menu()
        self.load_params()
        self.elo_graph_tab()

        self.setWindowTitle("Chess DB")
        self.show()

    # instantiates initial objects to run the program, starting with the config. If
    # this is first run, prompt will appear for chess.com username
    def load_params(self):
        # initial config instance
        self.config = config.Config()
        # prompt user for name, needed for database object
        try:
            self.user = self.config.settings["user"]
        except KeyError:
            name, ok = QInputDialog.getText(self, "Configuration", "Input your chess.com username:",
                                            QLineEdit.Normal)
            if ok and name != '':
                self.user = name
                self.config.settings["user"] = name
            else:
                self.exit()
        # initial query and db instances
        self.query = query.Query()
        self.db = database.Database(self.config.settings, default_query=self.query)

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        import_menu = menu.addMenu("Import")

        # QAction factory
        def create_action(name, action, hot_key=None):
            a = QAction(name, self)
            if hot_key is not None:
                a.setShortcut(hot_key)
            a.triggered.connect(action)
            return a

        file_menu.addAction(create_action(" Quit", self.exit, "Ctrl+Q"))
        import_menu.addAction(create_action("Import single file", self.import_game_file))
        import_menu.addAction(create_action("Import directory", self.import_directory))


    def create_tabs(self):
        pass

    def closeEvent(self, close):
        self.exit()

    # save settings and close database before exiting
    def exit(self):
        self.config.dump_settings()
        self.db.close()
        QCoreApplication.quit()

    ###### action methods ########

    #
    def import_game_file(self):
        options = QFileDialog.Options()
        options = QFileDialog.DontUseNativeDialog
        name, _ = QFileDialog.getOpenFileName(caption="Choose a single file", directory=os.getcwd(),
                                              options=options)
        if os.path.isfile(name):
            self.file_import(name)

    def import_directory(self):
        name = str(QFileDialog.getExistingDirectory(caption="Choose a directory", directory=os.getcwd()))
        print(name)
        if os.path.isdir(name):
            self.folder_import(name)

    # called to import files if user selects a whole directory
    def folder_import(self, folder):
        p = pgn.Pgn(self.config.settings, self.db)
        for file in os.listdir(folder):
            if file.endswith("pgn"):
                p.read_pgn(folder + "/" + file)

    # called to import a single file if user selects a single file
    def file_import(self, file):
        p = pgn.Pgn(self.config.settings, self.db)
        if str(file).endswith("pgn"):
            p.read_pgn(file)

    def elo_graph_tab(self):
        graph = GuiEloTab.EloGraph(self.db, self)
        self.setCentralWidget(graph)


if __name__ == '__main__':
    app = QApplication([])
    w = Chess()
    sys.exit(app.exec_())
