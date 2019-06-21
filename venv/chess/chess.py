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
                             QDialog, QLabel, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QFileDialog,
                             QInputDialog, QLineEdit, QFormLayout)

# Chess program files
import config
import database
import query
import pgn

# Program GUI widgets
import GuiEloTab
import GuiAnalysis


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
        self.load_params()

        # create initial tabs
        self.tabs = QTabWidget()

        #self.tab1 = QWidget()
        #self.tab2 = GuiEloTab.EloGraph(self.db)
        #self.tabs.addTab(self.tab1, "Main")
        #self.tabs.addTab(self.tab2, "ELO")
        self.setCentralWidget(self.tabs)
        self.create_tabs()
        # create the menu bar
        self.create_menu()



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

    def closeEvent(self, close):
        self.exit()

    # save settings and close database before exiting
    def exit(self):
        self.config.dump_settings()
        self.db.close()
        QCoreApplication.quit()

    # create the menu bar, add actions to the options, methods for actions below
    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        import_menu = menu.addMenu("Import")
        analysis_menu = menu.addMenu("Analysis")

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
        analysis_menu.addAction(create_action("Engine Path", self.set_engine_path))

    ###### action methods ########

    def import_game_file(self):
        options = QFileDialog.DontUseNativeDialog
        name, _ = QFileDialog.getOpenFileName(caption="Choose a single file", directory=os.getcwd(),
                                              options=options)
        if os.path.isfile(name):
            self.file_import(name)

    def import_directory(self):
        name = str(QFileDialog.getExistingDirectory(caption="Choose a directory", directory=os.getcwd()))
        # print(name)
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

    def set_engine_path(self):
        path, ok = QInputDialog.getText(self, "Configuration", "Path to engine executable:", QLineEdit.Normal)
        if ok:
            self.config.settings["engine"]["Path"] = path

    ####### Tab Methods #######

    def create_tabs(self):
        self.main_tab()
        self.elo_graph_tab()
        self.analysis_tab()

    def main_tab(self):
        main_tab = QWidget()
        layout = QFormLayout()
        lab = QLabel("""Welcome to chess db, if you would like to import games,do so through the menu bar import option. 
Currently pgn files are supported and chess.com files are likely the most effective.""")
        lab2 = QLabel("""Currently ELO by date or number of games played can be graphed in the Elo tab once games have 
been imported. Game analysis is in the Analysis tab, and will allow you to find moves you made that are a set distance 
from the move stockfish would have made. You can change this distance in the options menu.""")
        layout.addWidget(lab)
        layout.addWidget(lab2)
        main_tab.setLayout(layout)
        self.tabs.addTab(main_tab, "Main")

    def elo_graph_tab(self):
        graph = GuiEloTab.EloGraph(self.db)
        self.tabs.addTab(graph, "Elo")

    def analysis_tab(self):
        analysis = GuiAnalysis.Analysis(self.db, self.config.settings)
        self.tabs.addTab(analysis, "Analysis")


if __name__ == '__main__':
    app = QApplication([])
    w = Chess()
    sys.exit(app.exec_())
