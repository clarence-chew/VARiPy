from typing import Callable, Hashable
class ObserverSubject:
    def __init__(self):
        self.observers: dict[Hashable, set[Callable]] = dict()

    def register(self, key: Hashable, callback: Callable):
        self.observers[key] = self.observers.get(key, set())
        self.observers[key].add(callback)

    def unregister(self, key: Hashable, callback: Callable):
        if key in self.observers and callback in self.observers[key]:
            self.observers[key].remove(callback)

    def has_observers(self, key):
        return len(self.observers.get(key, set())) > 0

    def notify_observers(self, key: Hashable, *args, **kwargs):
        for observer in self.observers.get(key, set()):
            observer(*args, **kwargs)