from commons import get_tkinter_root

from controller.application import RemixController

def main():
    controller = RemixController()
    get_tkinter_root().mainloop()

if __name__ == "__main__":
    main()