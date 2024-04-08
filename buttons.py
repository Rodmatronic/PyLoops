import tkinter as tk
import pygame
from tkinter import ttk, filedialog
from tkinter import *
from PIL import Image, ImageTk
import math

class Light(tk.Canvas):
    def __init__(self, master, active_image_path, inactive_image_path, **kwargs):
        super().__init__(master, **kwargs)
        self.active_image = Image.open(active_image_path)
        self.inactive_image = Image.open(inactive_image_path)
        self.active = False

        # Create inactive state
        self.inactive_image = Image.open(inactive_image_path)  # Replace "your_inactive_image_path.jpg" with the path to your inactive image
        self.inactive_image = self.inactive_image.resize((10, 10))
        self.inactive_photo = ImageTk.PhotoImage(self.inactive_image)
        self.inactive_item = self.create_image(0, 0, anchor="nw", image=self.inactive_photo)

        # Create active state
        self.active_image = Image.open(active_image_path)  # Replace "your_active_image_path.jpg" with the path to your active image
        self.active_image = self.active_image.resize((10, 10))
        self.active_photo = ImageTk.PhotoImage(self.active_image)
        self.active_item = self.create_image(0, 0, anchor="nw", image=self.active_photo)
        
        # Hide active state initially
        self.itemconfig(self.active_item, state="hidden")

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.show_active()
        else:
            self.show_inactive()

    def show_active(self):
        self.itemconfig(self.active_item, state="normal")
        self.itemconfig(self.inactive_item, state="hidden")

    def show_inactive(self):
        self.itemconfig(self.active_item, state="hidden")
        self.itemconfig(self.inactive_item, state="normal")


class Custom_radio(tk.Canvas):
    def __init__(self, master, active_image_path, inactive_image_path, command, **kwargs):
        super().__init__(master, **kwargs)
        self.active_image = Image.open(active_image_path)
        self.inactive_image = Image.open(inactive_image_path)
        self.command = command
        self.active = False

        self.bind("<Button-1>", self.toggle)
        self.bind("<Button-3>", self.toggle)

        # Create inactive state
        self.inactive_photo = ImageTk.PhotoImage(self.inactive_image)
        self.inactive_item = self.create_image(0, 1, anchor="nw", image=self.inactive_photo)

        # Create active state
        self.active_photo = ImageTk.PhotoImage(self.active_image)
        self.active_item = self.create_image(0, 1, anchor="nw", image=self.active_photo)

        # Hide active state initially
        self.itemconfig(self.active_item, state="hidden")

    def toggle(self, event):
        self.active = not self.active
        if self.active:
            self.show_active()
        else:
            self.show_inactive()
        self.command()  # Only pass the active state, not event or any other arguments

    def toggle_normal(self):
        self.active = not self.active
        if self.active:
            self.show_active()
        else:
            self.show_inactive()
        self.command()  # Only pass the active state, not event or any other arguments

    def show_active(self):
        self.itemconfig(self.active_item, state="normal")
        self.itemconfig(self.inactive_item, state="hidden")

    def show_inactive(self):
        self.itemconfig(self.active_item, state="hidden")
        self.itemconfig(self.inactive_item, state="normal")

class Toggle_special_button(tk.Canvas):
    def __init__(self, master, active_image_path, inactive_image_path, command, **kwargs):
        super().__init__(master, **kwargs)
        self.active_image = Image.open(active_image_path)
        self.inactive_image = Image.open(inactive_image_path)
        self.command = command
        self.active = False

        self.bind("<Button-1>", self.toggle)
        self.bind("<Button-3>", self.toggle)

        # Create inactive state
        self.inactive_photo = ImageTk.PhotoImage(self.inactive_image)
        self.inactive_item = self.create_image(0, 1, anchor="nw", image=self.inactive_photo)

        # Create active state
        self.active_photo = ImageTk.PhotoImage(self.active_image)
        self.active_item = self.create_image(0, 1, anchor="nw", image=self.active_photo)

        # Hide active state initially
        self.itemconfig(self.active_item, state="hidden")

    def toggle(self, event):
        self.active = not self.active
        if self.active:
            self.show_active()
        else:
            self.show_inactive()
        self.command()  # Only pass the active state, not event or any other arguments

    def toggle_normal(self):
        self.active = not self.active
        if self.active:
            self.show_active()
        else:
            self.show_inactive()
        self.command()  # Only pass the active state, not event or any other arguments

    def show_active(self):
        self.itemconfig(self.active_item, state="normal")
        self.itemconfig(self.inactive_item, state="hidden")

    def show_inactive(self):
        self.itemconfig(self.active_item, state="hidden")
        self.itemconfig(self.inactive_item, state="normal")

class Knob(tk.Canvas):
    def __init__(self, master, bg_color, command, range=100, **kwargs):
        super().__init__(master, bg=bg_color, bd=0, **kwargs)  # Set border width to 0 to remove the outline
        self.bg_color = bg_color
        self.command = command
        self.range = range
        self.bind("<B1-Motion>", self.on_drag)
        self.sensitivity = 0.3  # Adjust this scaling factor to control sensitivity

        self.create_oval(32, 15, 32, 14, outline='#a9b5b5', width=3)

        # Load the knob image
        knob_image = Image.open("./UI/knob/knob.png")
        knob_image = knob_image.resize((30, 30))
        self.knob_image = ImageTk.PhotoImage(knob_image)

        # Draw the knob background image
        self.create_image(18, 18, image=self.knob_image)

    def on_drag(self, event):
        y = event.y
        if y < 0:
            y = 0
        elif y > 100:
            y = 100
        angle = self.get_angle(y)
        self.rotate(angle)
        value = int((angle / 300) * self.range)
        self.command(value)

    def rotate(self, angle):
        self.delete("indicator")
        line_length = 9  # Length of the white line
        self.create_line(15, 15, 15 + line_length * math.cos(math.radians(angle - 150)), 15 + line_length * math.sin(math.radians(angle - 150)),
                        fill='#94a1a7', tags="indicator", width=2)
        self.create_oval(14, 14, 14, 14, outline='#3f484d', width=6)
        print(f"{angle}")

    def get_angle(self, y):
        return int((y / 30) * 300 * self.sensitivity)  # Scale the angle by the sensitivity factor

class VolumeViewer(tk.Canvas):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(master, **kwargs)
        self.text = text
        self.command = command
        self.create_rectangle(0, 0, 30, 55, fill="#313538", outline="#313538")
        self.create_text(8, 6, text=text, fill="white", font=("Arial", 6))

class SmallButton(tk.Canvas):
    def __init__(self, master, bg_color, text, command, **kwargs):
        super().__init__(master, bg=bg_color, **kwargs)
        self.text = text
        self.command = command
        self.bind("<Button-1>", self.on_click)
        self.bind("<Button-3>", self.on_click)
        self.create_rectangle(0, 0, 15, 13, fill=bg_color, outline="#859798")
        self.create_text(8, 6, text=text, fill="Black", font=("Arial", 6))

    def on_click(self, event):
        self.command()

class CustomButton(tk.Canvas):
    def __init__(self, master, bg_color, toggle_color, toggle_command, sound_path, channel, **kwargs):
        super().__init__(master, bg=bg_color, **kwargs)
        self.bg_color = bg_color
        self.toggle_color = toggle_color
        self.toggle_command = toggle_command
        self.sound_path = sound_path
        self.channel = channel  # Add a new parameter for the channel
        self.bind("<Button-1>", self.on_click)
        self.bind("<Button-3>", self.on_click)

    def on_click(self, event):
        self.toggle_command()
        pygame.mixer.Channel(self.channel).play(pygame.mixer.Sound(self.sound_path))  # Specify the channel when playing the sound

class CustomDropdown(ttk.Combobox):
    def __init__(self, master=None, **kw):
        self.image = kw.pop('image', None)
        super().__init__(master, **kw)
        self.configure_button()
        
    def configure_button(self):
        # Hide the arrow
        self['state'] = 'readonly'
        self.bind_class("TCombobox", "<Button-1>", self.show_dropdown)
        
        # Center the text
        self.bind('<Configure>', self.center_text)
        
    def center_text(self, event=None):
        padding = ' ' * ((self.winfo_width() // self.font.measure('0')) // 2)
        self.set(padding + self.get().strip() + padding)
        
    def show_dropdown(self, event=None):
        self.event_generate('<Down>')
