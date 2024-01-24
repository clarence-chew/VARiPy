from commons.file import read_json_file, write_json_file, get_relative_path_if_in_cwd
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from model.settings import Settings

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

def browse_file(setting_var, callback=lambda: 0):
    file_path = askopenfilename()
    if file_path:
        setting_var.set(get_relative_path_if_in_cwd(file_path))
        callback()

class SettingsPanel(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.settings = None

    def create_widgets(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Configure row and column weights for resizing
        for i in range(3):
            self.columnconfigure(i, weight=1)

        # Creating labels and settings
        for idx, setting in enumerate(self.settings):
            value = setting.value

            # Right-align the labels in the left column
            label = tk.Label(self, text=setting.name, anchor="e")
            label.grid(row=idx, column=0, padx=5, pady=5, sticky="e")

            # Left-align the controls in the same column
            match setting.type:
                case "bool":
                    setting_element = tk.Checkbutton(self, variable=value)
                    setting_element.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
                    setting_element.bind("<ButtonRelease>", self.save_settings)
                case "int":
                    setting_element = ttk.Entry(self, textvariable=value, validate="key", validatecommand=(self.register(self.validate_int), "%P"))
                    setting_element.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
                case "path":
                    setting_element = tk.Entry(self, textvariable=value, state="readonly")
                    setting_element.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
                    browse_button = tk.Button(self, text="Browse",
                        command=lambda event=None, value=value: browse_file(value, self.save_settings))
                    browse_button.grid(row=idx, column=2, padx=5, pady=5, sticky="w")
                case "str":
                    setting_element = ttk.Entry(self, textvariable=value)
                    setting_element.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
                case other:
                    raise NotImplementedError(f"No UI implemented for setting '{other}'.")

            setting_element.bind("<Key>", self.save_settings)
            setting_element.bind("<FocusOut>", self.save_settings)
            setting_element.bind("<Control-c>", self.save_settings)
            setting_element.bind("<Control-v>", self.save_settings)

        # Bind <MouseWheel> event to the entire frame
        self.bind("<MouseWheel>", self.save_settings)

    def validate_int(self, new_value):
        try:
            int(new_value)
            return True
        except ValueError:
            return False

    def read_settings(self):
        if self.settings is not None:
            print("Warning: Settings have already been initialized.")
            return
        data = read_json_file("settings.json") or DEFAULT_SETTINGS
        self.settings = Settings(data)
        self.create_widgets()
    
    def save_settings(self, *_):
        write_json_file(self.settings.serialize(), "settings.json")

    def get(self, key, *default):
        return self.settings.get(key, *default)

if __name__ == "__main__":
    root = tk.Tk()
    notebook = ttk.Notebook(root)

    settings_panel = SettingsPanel(notebook)

    settings_panel.pack(fill=tk.BOTH, expand=True)
    notebook.add(settings_panel, text="Settings")
    notebook.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
