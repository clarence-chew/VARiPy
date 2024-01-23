from commons import get_tkinter_root
from config import DEFAULT_FILE
from model.music import Remix
from view import RemixView
from controller.application import RemixController

def main():
    model = Remix()
    view = RemixView()
    controller = RemixController(model, view)
    if DEFAULT_FILE:
        controller.read_data(DEFAULT_FILE)
    get_tkinter_root().mainloop()

if __name__ == "__main__":
    main()