"""
Performs start up operations, gets settings and completes initialization operations if first time
"""
# builtins
import json
import os


class Config:

    def __init__(self):
        self.settings_path = "items/settings.json"
        self.settings = dict()

        if not os.path.exists(self.settings_path):
            if not os.path.isdir("items"):
                os.mkdir("items")
            self.add_db_info()
            self.add_engine_info()
            self.add_analysis_info()
        else:
            try:
                with open(self.settings_path, 'r') as f:
                    self.settings = json.load(f)
            except exception as e:
                    print(e)

        self.dump_settings()

    def dump_settings(self):
        with open(self.settings_path, 'w') as f:
            json.dump(self.settings, f)

    def add_db_info(self):
        settings = self.settings
        db_info = dict()
        db_info["db_dir"] = "database"
        settings["database"] = db_info

    def add_engine_info(self):
        settings = self.settings
        engine_info = dict()
        engine_info["path"] = None
        settings["engine"] = engine_info

    def add_analysis_info(self):
        settings = self.settings
        analysis_info = dict()
        analysis_info["num_games"] = 50
        analysis_info["threshold"] = 1
        settings["analysis"] = analysis_info






