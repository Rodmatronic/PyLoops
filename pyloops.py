import tkinter as tk
import pygame
from tkinter import ttk, filedialog
from tkinter import *
from PIL import Image, ImageTk

import buttons
import dragwin
import mixer

version = 0.15
project_volume = 1
project_row_amount = 4
project_row_instrument_amount = 16
project_pitch = 0
is_mute = False
is_mono = False

instrument_canvas_show = True
proll_canvas_show = True
viewbrowser_canvas_show = True

# Define a dictionary to map instrument paths to fancy names
instrument_names = {
    'None': '--- Drum ---',
    './packs/drum/Kick1.wav': 'Kick Drum',
    './packs/drum/Cymbal1.wav': 'Crash',
    './packs/drum/Snare1.wav': 'Snare',
    './packs/drum/Clap1.wav': 'Clap',
    './packs/drum/Hi-hat1.wav': 'Hi-hat',

    "None1": '--- 808 ---',
    './packs/808-drum/808-kick.wav': '808 Kick',
    './packs/808-drum/808-clap.wav': '808 Clap',
    './packs/808-drum/808-hat.wav': '808 HiHat',
    './packs/808-drum/808-snare.wav': '808 Snare',
    './packs/808-drum/808-clav.wav': '808 Clav',
    './packs/808-drum/808-beep.wav': '808 Beep',
    './packs/808-drum/808-rim.wav': '808 Rim',
    './packs/808-drum/808-kick1.wav': '808 Kick 2',

    'None2': '--- FX ---',
    './packs/fx/bell.wav': 'FX Bell',
    './packs/fx/orchestra_hit.wav': 'FX Hit',
    './packs/fx/orchestra_low.wav': 'FX Hit Low',
    './packs/fx/timpani.wav': 'FX Timpani',
    './packs/fx/what.wav': 'FX What',
}

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

class LoopMakerApp:
    def selection_changed(self, event):
        selection = self.combo.get()
        print(f"Selected option: {selection}")

    def __init__(self, master):
        self.master = master
        self.master.title("PyLoops - New Project")
        self.master.configure(bg="#6a737b")
        self.master.geometry("1000x700")

        self.master.bind("<space>", self.toggle_play)

        # Initialize pygame mixer
        pygame.mixer.init(size=-16)
        pygame.mixer.set_num_channels(20)  # default is 8
        # Instantiate.

        combostyle = ttk.Style()

        combostyle.theme_create('combostyle', parent='alt',
        settings = {'TCombobox':
                    {'configure':
                    {'foreground': 'white',
                    'selectbackground': 'grey',
                    'fieldbackground': 'grey',
                    'background': 'grey'
                    }}}
        )
        # ATTENTION: this applies the new style 'combostyle' to all ttk.Combobox
        combostyle.theme_use('combostyle') 

        # Style for BPM entryrow
        combostyle.configure("Custom.TEntry", foreground="black", fieldbackground="#859798")

        # Create a custom canvas for controls
        self.controls_canvas = tk.Canvas(self.master, bg="#596267", highlightthickness=1, highlightbackground="black", border="2", height=75, width=800)
        self.controls_canvas.pack(fill=tk.X, anchor=N)

        # Create a custom canvas for the left Instrument pane
        self.viewbrowser_canvas = tk.Canvas(self.master, bg="#182126", highlightthickness=4, highlightbackground="#3f484d", border="3", height=1400, width=250)
        self.viewbrowser_canvas.place(x=0, y=80)

        self.create_windowed_canvases()
        self.draw_loop_canvas()
        self.draw_proll_canvas()
        self.drawdetails()

        # Add a button to open the .pyfl file
        self.open_file_button = tk.Button(self.viewbrowser_canvas, border=0, anchor="w", activebackground="#4c5459", activeforeground="White", bg="#182126", fg="#c3c9cd", highlightbackground="black", width=29, text="Open Project", command=self.open_pyfl_file)
        self.open_file_button.place(x=2, y=2)

        self.create_file_button = tk.Button(self.viewbrowser_canvas, border=0, anchor="w", activebackground="#4c5459", activeforeground="White", bg="#182126", fg="#c3c9cd", highlightbackground="black", width=29, text="Save as", command=self.create_pyfl_file)
        self.create_file_button.place(x=2, y=34)

        self.exit_sidebar = tk.Button(self.viewbrowser_canvas, border=0, anchor="w", activebackground="#4c5459", activeforeground="White", bg="#182126", fg="#c3c9cd", highlightbackground="black", width=29, text="Exit", command=exit)
        self.exit_sidebar.place(x=2, y=66)

        #self.new_file_sidebar = tk.Button(self.viewbrowser_canvas, border=0, anchor="w", activebackground="#4c5459", activeforeground="White", bg="#182126", fg="#c3c9cd", highlightbackground="black", width=29, text="New Project", command=exit)
        #self.new_file_sidebar.place(x=2, y=106)

        self.counter = 0
        self.interval = 100  # Interval in milliseconds
        self.timer_id = None

        self.playing = False
        self.play_button = tk.Button(self.controls_canvas, text="▶", activebackground="#4c5459", activeforeground="White", bg="#343c41", fg="#c3c9cd", highlightbackground="black", width=2, command=self.toggle_play)
        self.play_button.place(x=18, y=4)
        
        self.stop_button = tk.Button(self.controls_canvas, text="■", activebackground="#4c5459", activeforeground="White", bg="#343c41", fg="#c3c9cd", highlightbackground="black", width=2, command=self.stop_playing)
        self.stop_button.place(x=62, y=4)

        # Create a label for displaying the counter
        self.counter_label = tk.Label(self.controls_canvas, padx=17, text="0.00", bg="#859798", fg="Black", font=("Consolas", 14))
        self.counter_label.place(x=290, y=7)

        self.bpminput = ttk.Entry(self.controls_canvas, text='12', width=5, font=("Consolas", 15), style="Custom.TEntry")
        self.bpminput.place(x=125, y=5)
        self.bpminput.insert(0, "130")

        # Create small buttons
        self.up_button = buttons.SmallButton(self.controls_canvas, bg_color="#859798", text="▲", highlightthickness=0, width=16, height=10, command=self.increment_bpm)
        self.up_button.place(x=170, y=8)

        self.down_button = buttons.SmallButton(self.controls_canvas, bg_color="#859798", text="▼", highlightthickness=0, width=16, height=13, command=self.decrement_bpm)
        self.down_button.place(x=170, y=17)

        self.knobs_control()

        self.loop_button = buttons.Custom_radio(self.controls_canvas, inactive_image_path="./UI/buttons/inactive.png", active_image_path="./UI/buttons/active.png", bg="#596267", highlightthickness=0, width=19, height=19, command=self.toggle_loop)
        self.loop_button.place(x=127, y=42)

        self.looplabel = Label(text="Loop", bg="#596267", fg="White")
        self.looplabel.place(x=145, y=40)
        self.looping = False

        self.mono_button = buttons.Custom_radio(self.controls_canvas, inactive_image_path="./UI/buttons/inactive.png", active_image_path="./UI/buttons/active.png", bg="#596267", highlightthickness=0, width=19, height=17, command=self.set_mono)
        self.mono_button.place(x=127, y=62)

        self.mono_label = Label(text="Mono", bg="#596267", fg="White")
        self.mono_label.place(x=145, y=59)

        self.fadebutton = buttons.Custom_radio(self.controls_canvas, inactive_image_path="./UI/buttons/inactive.png", active_image_path="./UI/buttons/active.png", bg="#596267", highlightthickness=0, width=19, height=17, command=self.set_mono)
        self.fadebutton.place(x=192, y=42)

        self.fadelabel = Label(text="Fade out", bg="#596267", fg="White")
        self.fadelabel.place(x=210, y=39)

        self.mutebutton = buttons.Custom_radio(self.controls_canvas, inactive_image_path="./UI/buttons/inactive.png", active_image_path="./UI/buttons/active.png", bg="#596267", highlightthickness=0, width=19, height=17, command=self.mute)
        self.mutebutton.place(x=192, y=62)

        self.mutelabel = Label(text="Mute", bg="#596267", fg="White")
        self.mutelabel.place(x=210, y=59)

        self.instrument_canvas_toggle = buttons.Toggle_special_button(self.controls_canvas, inactive_image_path="./UI/special-buttons/channel_active.png", active_image_path="./UI/special-buttons/channelicon.png", bg="#596267", highlightthickness=0, width=30, height=35, command=self.toggle_channel_rack)
        self.instrument_canvas_toggle.place(x=290, y=43)

        self.proll_canvas_toggle = buttons.Toggle_special_button(self.controls_canvas, inactive_image_path="./UI/special-buttons/proll_active.png", active_image_path="./UI/special-buttons/prollicon.png", bg="#596267", highlightthickness=0, width=30, height=35, command=self.toggle_proll)
        self.proll_canvas_toggle.place(x=323, y=43)

        self.viewbrowser_canvas_toggle = buttons.Toggle_special_button(self.controls_canvas, inactive_image_path="./UI/special-buttons/viewpicker_active.png", active_image_path="./UI/special-buttons/viewpicker.png", bg="#596267", highlightthickness=0, width=30, height=35, command=self.toggle_viewbrowser)
        self.viewbrowser_canvas_toggle.place(x=356, y=43)

        #self.vollumeviewer = buttons.VolumeViewer(self.controls_canvas, text=10, bg="#4a5252", highlightthickness=0, width=40, height=75, command=self.toggle_loop)
        #self.vollumeviewer.place(x=420, y=10)

        #self.add_row_button = Button(self.master, text="+", command=self.add_row)
        #self.add_row_button.place(x=100, y=81 + project_row_amount*30 + 40)  # Adjusted position

        #self.remove_row_button = Button(self.master, text="-", command=self.remove_row)
        #self.remove_row_button.place(x=140, y=81 + project_row_amount*30 + 40)  # Adjusted position

        # Create the grid of buttons
        self.cells = [[0] * project_row_instrument_amount for _ in range(project_row_amount)]  # 4 rows, 16 columns
        self.create_grid(project_row_amount)

    def create_windowed_canvases(self):
        self.loop_canvas = dragwin.DraggableCanvas(self.master, self.controls_canvas, bg="#5f686d", highlightthickness=4, highlightbackground="#3f484d", border="3", height=180, width=500)
        self.loop_canvas.place(x=280, y=100)

        self.proll_canvas = dragwin.DraggableCanvas(self.master, self.controls_canvas, bg="#333544", highlightthickness=4, highlightbackground="#3f484d", border="3", height=300, width=600)
        self.proll_canvas.place(x=280, y=300)

    def draw_loop_canvas(self):
        self.loop_canvas.create_rectangle(0, 0, 1080, 29, fill="#3f484d", width=0)

        self.loop_label = tk.Label(self.loop_canvas, text="Channel rack", bg="#3f484d", fg="white")
        self.loop_label.place(x=10, y=8)

        self.loop_close_button = buttons.Custom_radio(self.loop_canvas, width=14, height=14, active_image_path="./UI/buttons/close.png", bg="#3f484d", inactive_image_path="./UI/buttons/close.png", highlightthickness=0, command=self.close_instrument_canvas)
        self.loop_close_button.place(x=485, y=9)

    def draw_proll_canvas(self):
        # Load and display an image 
        image = Image.open('./UI/keyb/keyb.bmp')
        photo_image = ImageTk.PhotoImage(image)

        # Create a label to display the image
        image_label = tk.Label(self.proll_canvas, image=photo_image)
        image_label.photo = photo_image  # Keep a reference to the PhotoImage object
        image_label.place(x=6, y=30)

        # Create a label to display the image
        image_label1 = tk.Label(self.proll_canvas, image=photo_image)
        image_label1.photo = photo_image  # Keep a reference to the PhotoImage object
        image_label1.place(x=6, y=175)

        # Create a label to display the image
        image_label2 = tk.Label(self.proll_canvas, image=photo_image)
        image_label2.photo = photo_image  # Keep a reference to the PhotoImage object
        image_label2.place(x=6, y=200)

        self.proll_canvas.create_rectangle(0, 0, 1080, 29, fill="#3f484d", width=0)

        self.proll_label = tk.Label(self.proll_canvas, text="Piano roll", bg="#3f484d", fg="white")
        self.proll_label.place(x=10, y=8)

        self.proll_close_button = buttons.Custom_radio(self.proll_canvas, width=14, height=14, active_image_path="./UI/buttons/close.png", bg="#3f484d", inactive_image_path="./UI/buttons/close.png", highlightthickness=0, command=self.close_proll_canvas)
        self.proll_close_button.place(x=585, y=9)


    def drawdetails(self):
        self.controls_canvas.create_line(18,65,18,77, fill="#40494e", width=2)
        self.controls_canvas.create_line(18,77,107,77, fill="#40494e", width=2)
        self.controls_canvas.create_line(107,65,107,77, fill="#40494e", width=2)

        self.controls_canvas.create_line(10,0,10,200, fill="#40494e", width=2)
        self.controls_canvas.create_line(115,0,115,200, fill="#40494e", width=2)

        self.controls_canvas.create_line(280,0,280,200, fill="#40494e", width=2)

        self.controls_canvas.create_line(280,39,1200,39, fill="#40494e", width=2)

    def toggle_viewbrowser(self):
        global viewbrowser_canvas_show
        if viewbrowser_canvas_show == True:
            self.close_viewbrowser_canvas()
            viewbrowser_canvas_show = False
        else:
            self.viewbrowser_canvas.place(x=0, y=80)
            viewbrowser_canvas_show = True

    def toggle_channel_rack(self):
        global instrument_canvas_show
        if instrument_canvas_show == True:
            self.close_instrument_canvas()
            instrument_canvas_show = False
        else:
            self.loop_canvas.place(x=280, y=100)
            instrument_canvas_show = True

    def toggle_proll(self):
        global proll_canvas_show
        if proll_canvas_show == True:
            self.close_proll_canvas()
            proll_canvas_show = False
        else:
            self.proll_canvas.place(x=280, y=300)
            proll_canvas_show = True

    def close_viewbrowser_canvas(self):
        self.viewbrowser_canvas.place_forget() 

    def close_proll_canvas(self):
        self.proll_canvas.place_forget() 

    def close_instrument_canvas(self):
        self.loop_canvas.place_forget() 

    def knobs_control(self):
        self.volume_knob = buttons.Knob(self.controls_canvas, bg_color="#596267", width=35, height=33, highlightthickness=0, command=self.volume_changed)
        self.volume_knob.place(x=26, y=42)
        self.volume_knob.rotate(0)  # Set initial position
        self.volume_knob.rotate(300)  # Set initial position

        self.light_volume = buttons.Light(self.controls_canvas, bg="#596267", inactive_image_path='./UI/indicators/light_off.png', active_image_path='./UI/indicators/light_on.png', width=10, height=10, highlightthickness=0)
        self.light_volume.place(x=18, y=52)
        self.light_volume.show_active()

        self.offset_knob = buttons.Knob(self.controls_canvas, bg_color="#596267", width=35, height=33, highlightthickness=0, command=donothing)
        self.offset_knob.place(x=68, y=42)
        self.offset_knob.rotate(0)  # Set initial position

    def mute(self):
        global is_mute
        global project_volume
        if is_mute:
            print("unmute")
            project_volume = 1
            is_mute = False
        else:
            print("mute")
            project_volume = 0
            is_mute = True

    def update_counter(self):
        self.counter += 0.01  # Increment the counter by 0.01 for decimal counting
        # Update the counter label with the current counter value
        self.counter_label.config(text=f"{self.counter:.2f}")
        self.timer_id = self.master.after(self.interval, self.update_counter)

    def reset_counter(self):
        self.counter = 0
        # Reset the counter label
        self.counter_label.config(text="0.00")

    def increment_bpm(self):
        current_bpm = int(self.bpminput.get())
        self.bpminput.delete(0, tk.END)
        self.bpminput.insert(0, str(current_bpm + 1))
        if current_bpm > 500:
            current_bpm = 500

    def decrement_bpm(self):
        current_bpm = int(self.bpminput.get())
        self.bpminput.delete(0, tk.END)
        self.bpminput.insert(0, str(current_bpm - 1))

    def toggle_loop(self):
        self.looping = not self.looping
        if self.looping:
            self.loop_button.config(relief=tk.SUNKEN)
        else:
            self.loop_button.config(relief=tk.RAISED)

    def set_mono(self):
        if is_mono == False:
            pygame.mixer.stop()
        else:
            pygame.mixer.stop()

    def get_bpm(self):
        try:
            return int(self.bpminput.get())
        except ValueError:
            return 120  # Default BPM if input is invalid
        
    def create_grid(self, num_rows=12):
        self.indicators = []
        self.instrument_dropdowns = []
        self.indicators_vertical = []
        channels = list(range(num_rows))  # Define the channels for each row
        
        # Keep track of used instrument indices
        used_indices = set()

        for i in range(num_rows):
            indicator_row = []
            dropdown_row = []
            for j in range(project_row_instrument_amount):
                color = "grey" if (j // 4) % 2 == 0 else "#843942"
                sound_path = f"./packs/default-start-pl/{i + 1}.wav"  # Replace with your sound file paths
                channel = channels[i]  # Assign the channel for this row
                cell = buttons.CustomButton(self.loop_canvas, width=14, height=20, bg_color=color,
                                    toggle_color="orange", toggle_command=lambda i=i, j=j: self.toggle_cell(i, j),
                                    sound_path=sound_path, channel=channel, highlightthickness=1, highlightbackground="black")
                # Calculate x position for the cell
                x_pos = 170 + (j * 18)  # Starting X position of 80, with cells spaced 18 pixels apart
                cell.place(x=x_pos, y=25 + i*30 + 20)  # Adjusted y-coordinate based on the row, with 90 pixel gap before the first row

                self.cells[i][j] = (cell, color)  # Storing cell and original color

                # Calculate x position for the indicator
                indicator_x_pos = 154 + ((j+1) * 18)  # Starting X position of 50, with indicators spaced 10 pixels apart
                indicator_y_pos = 28 + i*30 + 20  # Adjusted y-coordinate based on the current grid Y position
                indicator = tk.Canvas(self.loop_canvas, width=10, height=2, bg="#794138", highlightbackground="#050505", highlightthickness=1)  # Set initial color to red
                indicator.place(y=indicator_y_pos, x=indicator_x_pos)
                indicator_row.append(indicator)
            self.indicators.append(indicator_row)

            # Create instrument dropdown for each row
            instruments = list(instrument_names.values())
            
            # Find the next available index for the dropdown
            index = 7
            while index in used_indices:
                index += 1
            used_indices.add(index)

            # Set values for dropdown
            instrument_dropdown = ttk.Combobox(self.loop_canvas, values=instruments, width=9)
            instrument_dropdown.current(index)
            instrument_dropdown['state'] = 'readonly'
            instrument_dropdown.bind("<<ComboboxSelected>>", lambda event, row=i, dropdown=instrument_dropdown: self.instrument_changed(row, dropdown))
            instrument_dropdown.place(x=65, y=45 + i*30)
            dropdown_row.append(instrument_dropdown)
            self.instrument_dropdowns.append(dropdown_row)

            self.disable_button = buttons.Custom_radio(self.loop_canvas, inactive_image_path="./UI/buttons/inactive.png", active_image_path="./UI/special-buttons/active.png", bg="#5f686d", highlightthickness=0, width=19, height=19, command=donothing)
            self.disable_button.place(x=11, y=49 + i*30)

            volume_knob = buttons.Knob(self.loop_canvas, bg_color="#5f686d", width=35, height=30, highlightthickness=0, command=lambda value, row=i: donothing)
            volume_knob.place(x=29, y=40 + i*30)
            volume_knob.rotate(150)  # Set initial position

            self.disable_button.toggle_normal()

    #def toggle_row(self):
    def volume_changed(self, value):
        global project_volume
        project_volume = value / 100  # Update the project volume
        print("Volume value:", project_volume)
        if project_volume == 0:
            self.light_volume.show_inactive()
        if project_volume > 0:
            self.light_volume.show_active()
        # Adjust the volume for all channels
        for channel_index in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(channel_index).set_volume(project_volume)


    def add_row(self):
        global project_row_amountF
        project_row_amount += 1
        # Move add and remove buttons down by 20 pixels
        self.add_row_button.place(y=self.add_row_button.winfo_y() + 30)
        self.remove_row_button.place(y=self.remove_row_button.winfo_y() + 30)
        
        # Append a new row to self.cells
        self.cells.append([0] * project_row_instrument_amount)
        
        # Recreate the grid with the updated number of rows
        self.create_grid(project_row_amount)

    def remove_row(self):
        num_rows = len(self.cells)
        if num_rows > 0:
            global project_row_amount
            project_row_amount -= 1
            # Move add and remove buttons up by 20 pixels
            self.add_row_button.place(y=self.add_row_button.winfo_y() - 20)
            self.remove_row_button.place(y=self.remove_row_button.winfo_y() - 20)
            
            # Remove the last row from self.cells
            self.cells.pop()
            
            # Recreate the grid with the updated number of rows
            self.create_grid(project_row_amount)

    def toggle_cell(self, row, col):
        cell, original_color = self.cells[row][col]
        if cell.bg_color == original_color:
            if original_color == "#843942":
                cell.configure(bg="#F48693", highlightbackground="#f76a6a")  # Activated color

            if original_color == "grey":
                cell.configure(bg="#dfdfdf", highlightbackground="#c7c7c7")  # Activated color
            cell.bg_color = "orange"
        else:
            cell.configure(bg=original_color, highlightbackground="black")
                # Deactivated color
            cell.bg_color = original_color

    def instrument_changed(self, row, dropdown):
        selected_fancy_name = dropdown.get()
        for col in range(project_row_instrument_amount):
            cell, _ = self.cells[row][col]
            sound_path = next(path for path, name in instrument_names.items() if name == selected_fancy_name)
            cell.sound_path = sound_path

    def toggle_play(self, event=None):
        if self.playing:
            self.stop_playing()
            self.play_button.config(relief=tk.RAISED)
            self.reset_counter()
        else:
            self.play_button.config(text="▍▍")
            self.play_button.config(relief=tk.SUNKEN)
            self.playing = True
            self.animate_indicators()
            self.start_counter()

    def start_counter(self):
        self.timer_id = self.master.after(self.interval, self.update_counter)

    def stop_counter(self):
        if self.timer_id:
            self.reset_counter()
            self.master.after_cancel(self.timer_id)

    def stop_playing(self):
        self.play_button.config(relief=tk.RAISED)
        self.playing = False
        self.play_button.config(text="▶")
        self.stop_counter()

    def animate_indicators(self, col=0):
        if col >= project_row_instrument_amount or not self.playing:
            if self.looping:
                if not self.playing:
                    self.stop_playing()
                    return
                col = 0  # Restart from the beginning when looping
                self.reset_counter()
            else:
                self.stop_playing()
                return

        for row in range(4):
            if self.cells[row][col][0].bg_color == "orange":
                try:
                    sound = pygame.mixer.Sound(self.cells[row][col][0].sound_path)
                    sound.set_volume(project_volume)  # Set the volume level here
                    sound.play()
                except:
                    pass
            self.indicators[row][col].configure(bg="#ed6140")
            self.master.update_idletasks()

        bpm = self.get_bpm()
        interval = int((60 / bpm) * 250)  # Interval in milliseconds

        self.master.after(interval, self.clear_indicators, col)


    def clear_indicators(self, col):
        for row in range(4):
            self.indicators[row][col].configure(bg="#794138")
        self.master.update_idletasks()
        self.master.after(0, self.animate_indicators, col + 1)

    def open_pyfl_file(self):
        # Ask the user to choose the file to open
        file_path = filedialog.askopenfilename(filetypes=[("PyFL Files", "*.pyfl")])

        self.master.title(f"PyLoops - {file_path}")
        if file_path:
            # Read the content of the file
            with open(file_path, "r") as file:
                lines = file.readlines()

            instrument_index = 0

            for line in lines:
                if "bpm:" in line:
                    index = line.index("bpm:") + len("bpm:")
                    bpm = int(line[index:index + 3])  # Assuming BPM is represented by 3 bytes
                    print(f"BPM: {bpm}")
                    self.bpminput.delete(0, 'end')
                    self.bpminput.insert(0, str(bpm))

                if "loop:" in line:
                    looping_value = line.split(":")[1].strip()  # Get the value after "loop:" and remove whitespace
                    if looping_value.lower() == "true":
                        if self.looping == True:
                            print("file_loop: Already True")
                        else:
                            print("file_loop: True")
                            self.loop_button.toggle_normal()
                    elif looping_value.lower() == "false":
                        print("False")
                        self.looping = False
                    else:
                        print("Invalid looping value found in the file:", looping_value)

            for line_index, line in enumerate(lines):
                if not line.strip():
                    continue  # Skip empty lines

                if "Instrument:" in line:
                    # Extract instrument name and set it for the corresponding dropdown
                    instrument_name = line.split(":")[1].strip()
                    if instrument_name in instrument_names.values():
                        index = list(instrument_names.values()).index(instrument_name)
                        dropdown = self.instrument_dropdowns[instrument_index][0]
                        dropdown.current(index)

                        # Update the instrument for the current and next row
                        self.instrument_changed(instrument_index, dropdown)
                        if line_index < len(lines) - 1:
                            self.instrument_changed(instrument_index + 1, dropdown)

                        instrument_index += 1
                    else:
                        print("Invalid instrument name found in the file:", instrument_name)
                else:
                    # Update the grid cells based on the content of the file
                    channel_data = line.strip().split(", ")
                    for j, value in enumerate(channel_data):
                        if value == "1":
                            # Determine the color based on the position in the row
                            if (j // 4) % 2 == 0:
                                # Set the cell to activated color (grey)
                                self.cells[instrument_index][j][0].configure(bg="#dfdfdf", highlightbackground="#c7c7c7")
                            else:
                                # Set the cell to activated color (red)
                                self.cells[instrument_index][j][0].configure(bg="#F48693", highlightbackground="#f76a6a")
                            self.cells[instrument_index][j][0].bg_color = "orange"
                        else:
                            # Set the cell to its original color
                            original_color = self.cells[instrument_index][j][1]
                            self.cells[instrument_index][j][0].configure(bg=original_color, highlightbackground="black")
                            self.cells[instrument_index][j][0].bg_color = original_color

    def create_pyfl_file(self):
        # Get the grid data and generate the file content
        file_content = ""
        for i, row in enumerate(self.cells):
            channel_data = ", ".join("1" if cell.bg_color == "orange" else "0" for cell, _ in row)
            file_content += f"{channel_data}\n"

            # Get the selected instrument for the current row
            selected_instrument = self.instrument_dropdowns[i][0].get()
            file_content += f"Instrument: {selected_instrument}\n"  # Add instrument information

        # Add BPM and loop information
        bpm = int(self.bpminput.get())
        file_content += f"bpm:{bpm}\n"

        islooping = self.looping
        file_content += f"loop:{islooping}\n"

        # Ask the user to choose the save location
        file_path = filedialog.asksaveasfilename(defaultextension=".pyfl", filetypes=[("PyFL Files", "*.pyfl")])
        if file_path:
            # Write the content to the file
            with open(file_path, "w") as file:
                file.write(file_content)


def donothing():
    x = 0

# Define the animation function
def animate_logo(label, img, width, height):
    angle = -120
    for i in range(24, 270, 10):  # Change the range to adjust the animation speed
        resize_image = img.resize((i, i))
        rotated_image = resize_image.rotate(angle)  # Rotate the image
        new_img = ImageTk.PhotoImage(rotated_image)
        label.configure(image=new_img)
        label.image = new_img
        label.place(x=(width - i) // 2, y=(height - i) // 2)
        label.update()
        angle += 4  # Increase the angle for rotation
    for i in range(270, 290, 6):  # Change the range to adjust the animation speed
        resize_image = img.resize((i, i))
        rotated_image = resize_image.rotate(angle)  # Rotate the image
        new_img = ImageTk.PhotoImage(rotated_image)
        label.configure(image=new_img)
        label.image = new_img
        label.place(x=(width - i) // 2, y=(height - i) // 2)
        label.update()
        angle += 3  # Increase the angle for rotation
    for i in range(290, 310, 4):  # Change the range to adjust the animation speed
        resize_image = img.resize((i, i))
        rotated_image = resize_image.rotate(angle)  # Rotate the image
        new_img = ImageTk.PhotoImage(rotated_image)
        label.configure(image=new_img)
        label.image = new_img
        label.place(x=(width - i) // 2, y=(height - i) // 2)
        label.update()
        angle += 1  # Increase the angle for rotatin
    for i in range(310, 320, 1):  # Change the range to adjust the animation speed
        resize_image = img.resize((i, i))
        rotated_image = resize_image.rotate(angle)  # Rotate the image
        new_img = ImageTk.PhotoImage(rotated_image)
        label.configure(image=new_img)
        label.image = new_img
        label.place(x=(width - i) // 2, y=(height - i) // 2)
        label.update()
        angle += 0.5  # Increase the angle for rotation

def about_window():
    about_window = tk.Toplevel()
    about_window.title("About")    
    about_window.configure(bg="#5a6970")

    about_window.geometry("520x420")

    image = Image.open("./UI/logos/berry.png")
    resize_image = image.resize((300, 300))
    img = ImageTk.PhotoImage(resize_image)
 
    # create label and add resize image
    label1 = Label(about_window, image=img, bg="#5a6970")
    label1.image = img
    width, height = 300, 300  # Adjust according to the desired position of the logo
    label1.place(x=(width - 50) // 2, y=(height - 50) // 2)

    # Add text
    text_label = tk.Label(about_window, bg="#5a6970", fg="#5a6970", text=f"PL Studio {version}", font="Modern 22 bold")
    text_label.place(x=270, y=60)
    
    small_text_label = tk.Label(about_window, bg="#5a6970", fg="#5a6970", text="Written by Rodmatronics", font=("Modern", 12))
    small_text_label.place(x=270, y=98)

    thanks_label = tk.Label(about_window, bg="#5a6970", fg="#5a6970", text="Special thanks to:\n\n4vul\n\nEcstaticoder\n\nAnd the lovely folks at Python", font=("Modern", 10))
    thanks_label.place(x=270, y=125)


    # Define the fade-in animation for the text
    def fade_in_text(step=90):
        if step <= 255:
            # Convert step value to hexadecimal and make sure it's always two characters
            step_hex = format(step, '02x')
            # Construct the color in hexadecimal format
            color = f'#{step_hex*3}'  # RRGGBB
            # Update text color
            text_label.config(fg=color)
            small_text_label.config(fg=color)
            thanks_label.config(fg=color)
            # Schedule the next iteration
            about_window.after(1, fade_in_text, step + 1)

    # Start the fade-in animation
    fade_in_text()

    animate_logo(label1, image, width, height)


def createmenubar(root, app):
    def randomize_buttons():
        import random
        for row in app.cells:
            for cell, original_color in row:
                if random.choice([True, False]):
                    if cell.bg_color == original_color:
                        if original_color == "#843942":
                            cell.configure(bg="#F48693", highlightbackground="#f76a6a")  # Activated color
                        if original_color == "grey":
                            cell.configure(bg="#dfdfdf", highlightbackground="#c7c7c7")  # Activated color
                        cell.bg_color = "orange"
                    else:
                        cell.configure(bg=original_color, highlightbackground="black")  # Deactivated color
                        cell.bg_color = original_color

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    editmenu = tk.Menu(menubar, tearoff=0)
    editmenu.add_command(label="Randomize", command=randomize_buttons)  # Add Randomize command
    menubar.add_cascade(label="Edit", menu=editmenu)

    toolmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Tools", menu=toolmenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=about_window)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)


def main():
    root = tk.Tk()
    app = LoopMakerApp(root)
    createmenubar(root, app)
    root.mainloop()

if __name__ == "__main__":
    main()
