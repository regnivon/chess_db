"""
Performs start up operations, gets settings and initalizes if first time
"""
import json

class Config:

    def __init__(self):
        self.settings_path = "items/settings.json"
