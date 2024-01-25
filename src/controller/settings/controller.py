from model.settings import SettingValue, Settings
from view import SettingsPanel
from commons.file import read_json_file, write_json_file

DEFAULT_SETTINGS = {
    # Settings on load
    "DEFAULT_FILE": {
        "name": "Default File",
        "type": "path",
        "value": "examples/example.txt"
    },
    # Behaviour
    "DISCARD_NEGLIGIBLE_SECTIONS": {
        "name": "Discard Negligible Sections",
        "type": "bool",
        "value": True
    },
    "RESTART_ON_JS_ERROR": {
        "name": "Restart on JavaScript Error",
        "type": "bool",
        "value": False
    },
    "ROBUST_TO_LAG": {
        "name": "Robust to Lag",
        "type": "bool",
        "value": False
    },
    "FLUSH_JAVASCRIPT": {
        "name": "Refresh Page to Set JavaScript",
        "type": "bool",
        "value": False
    },
    # UI settings
    "TRACK_HEIGHT": {
        "name": "Track Height",
        "type": "int",
        "value": 30
    },
    "MIN_WINDOW_WIDTH": {
        "name": "Min Window Width",
        "type": "int",
        "value": 500
    },
    "MIN_WINDOW_HEIGHT": {
        "name": "Min Window Height",
        "type": "int",
        "value": 300
    }
}

class SettingsController:
    def __init__(self, view: SettingsPanel):
        self.view = view
    
    def initialize_data(self):
        self.view.read_settings("settings.json", default=DEFAULT_SETTINGS)

    def get_setting(self, key, *default):
        return self.view.get(key, *default)