from model.settings import SettingValue, Settings
from view import SettingsPanel
from commons.file import read_json_file, write_json_file

class SettingsController:
    def __init__(self, view: SettingsPanel):
        self.view = view
    
    def initialize_data(self):
        self.view.read_settings()

    def get_setting(self, key, *default):
        return self.view.get(key, *default)