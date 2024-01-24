from commons import get_tkinter_root
from model.music import Remix
from view import RemixView
from controller.application import RemixController

def main():
    model = Remix()
    view = RemixView()
    controller = RemixController(model, view)
    get_tkinter_root().mainloop()

if __name__ == "__main__":
    main()