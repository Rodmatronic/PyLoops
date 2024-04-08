import tkinter as tk
import pygame
import pyflp
from tkinter import ttk, filedialog
from tkinter import *
from PIL import Image, ImageTk

class DraggableCanvas(tk.Canvas):
    def __init__(self, master, controls_canvas, **kwargs):
        super().__init__(master, **kwargs)
        self.controls_canvas = controls_canvas
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self._drag_data = {'x': event.x, 'y': event.y}

    def on_drag(self, event):
        new_x = self.winfo_x() + (event.x - self._drag_data['x'])
        new_y = self.winfo_y() + (event.y - self._drag_data['y'])
        if not self.check_collision(new_x, new_y):
            self.place(x=new_x, y=new_y)
        else:
            self.on_release()

    def on_release(self):
        self.event_generate('<ButtonRelease-1>')


    def check_collision(self, x, y):
        x1, y1, x2, y2 = self.controls_canvas.winfo_x(), self.controls_canvas.winfo_y(), \
                         self.controls_canvas.winfo_x() + self.controls_canvas.winfo_width(), \
                         self.controls_canvas.winfo_y() + self.controls_canvas.winfo_height()
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
        return False
