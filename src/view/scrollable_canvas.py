from commons import subdictionary
import tkinter as tk

CANVAS_VALID_KWARGS = ["background", "bg", "borderwidth", "bd", "closeenough", "confine", "cursor", "height", "highlightbackground", "highlightcolor", "highlightthickness", "insertbackground", "insertborderwidth", "insertontime", "insertontime", "insertwidth", "relief", "scrollregion", "selectbackground", "selectborderwidth", "selectforeground", "state", "takefocus", "width", "xscrollcommand", "xscrollincrement", "yscrollcommand", "yscrollincrement"]

class ScrollableCanvas(tk.Frame):
    def __init__(self, master=None, canvas_class=tk.Canvas, **kwargs):
        super().__init__(master)
        self.master = master
        
        self.canvas_width = kwargs["width"]
        self.canvas_height = kwargs["height"]

        # Create a custom canvas and scrollbars
        self.canvas = canvas_class(self, scrollregion=(0, 0, self.canvas_width, self.canvas_height), **subdictionary(kwargs, CANVAS_VALID_KWARGS))
        h_scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        v_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Pack the canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind the canvas to the mouse wheel for vertical scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-event.delta // 120, "units")

    def resize_canvas_to_content(self):
        # Get the bounding box of all items on the canvas
        bbox = self.canvas.bbox("all")

        new_width = bbox[2]
        new_height = bbox[3]

        self.canvas.config(scrollregion=(0, 0, new_width, new_height),
            width=self.canvas_width, height=self.canvas_height)

