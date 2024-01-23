from tkinter import BooleanVar, StringVar
from typing import Any
from weakref import WeakSet

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
        self.observers = dict()
        for key, value in self.settings.items():
            value.register(lambda *args, key=key: self.notify_observers(key))

    def serialize(self):
        return { key: value.serialize() for key, value in self.settings.items() }

    def __iter__(self):
        return iter(self.settings.values())
    def get(self, key, *default):
        if key in self.settings:
            return self.settings[key].value.get()
        if default:
            return default
        raise KeyError(key)

    def register(self, key, observer):
        self.observers[key] = self.observers.get(key, WeakSet())
        self.observers[key].add(observer)

    def unregister(self, key, observer):
        self.observers[key].remove(observer)

    def notify_observers(self, key):
        for observer in self.observers.get(key, WeakSet()):
            observer()
