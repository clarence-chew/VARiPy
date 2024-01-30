from tkinter import BooleanVar, StringVar, Variable
from typing import Any
from commons.observer import ObserverSubject

class DictVar(Variable):
    def __init__(self, master=None, value=None, name=None):
        super().__init__(master=master, name=name)
        self.value = dict(value)
    def get(self):
        return dict(self.value)
    def get_key(self, key, *default):
        return self.value.get(key, *default)
    def set(self, value):
        self.value = dict(value)
    def set_key(self, key, value):
        self.value[key] = value
    def trace_add(self, mode, callback):
        super().trace_add(mode, callback)
    def trace_info(self):
        return super().trace_info()
    def trace_remove(self, mode, cbname):
        super().trace_remove(mode, cbname)

def create_observable_value(type, value):
    if type == "bool":
        return BooleanVar(value=bool(value))
    return StringVar(value=str(value))

class SettingValue:
    name: str
    type: str
    value: Any
    def __init__(self, json):
        self.name = json["name"]
        self.type = json["type"]
        value = json["value"]
        self.value_type = type(value)
        self.value = create_observable_value(json["type"], value)
    def register(self, callback):
        self.value.trace_add("write", callback)
    def serialize(self):
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value_type(self.value.get())
        }

class Settings:
    def __init__(self, json):
        self.settings = { key: SettingValue(value) for key, value in json.items() }
        self.observer_subject = ObserverSubject()
        for key, value in self.settings.items():
            value.register(lambda *args, key=key: self.observer_subject.notify_observers(key))

    def serialize(self):
        return { key: value.serialize() for key, value in self.settings.items() }

    def __iter__(self):
        return iter(self.settings.items())

    def get(self, key, *default):
        if key in self.settings:
            return self.settings[key].value.get()
        if default:
            return default
        raise KeyError(key)

    def register(self, key, observer):
        self.observer_subject.register(key, observer)

    def unregister(self, key, observer):
        self.observer_subject.unregister(key, observer)

    def notify_observers(self, key, *args, **kwargs):
        self.observer_subject.notify_observers(key, *args, **kwargs)
