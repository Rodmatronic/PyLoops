import tkinter as tk
from tkinter import ttk
import pygame

class CustomButton(tk.Canvas):
    def __init__(self, master, bg_color, toggle_color, toggle_command, sound_path, **kwargs):
        super().__init__(master, bg=bg_color, **kwargs)
        self.bg_color = bg_color
        self.toggle_color = toggle_color
        self.toggle_command = toggle_command
        self.sound_path = sound_path
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.toggle_command()
        pygame.mixer.Sound(self.sound_path).play()


class LoopMakerApp:

    def selection_changed(self, event):
        selection = self.combo.get()
        print(f"Selected option: {selection}")

    def __init__(self, master):
        self.master = master
        self.master.title("PyLoops")
        self.master.configure(bg="#5a6970")
        self.master.geometry("390x270")
        # Initialize pygame mixer
        pygame.mixer.init()

        self.playing = False
        self.play_button = tk.Button(self.master, text="Play", command=self.toggle_play)
        self.play_button.grid(row=0, column=0, columnspan=1, pady=20)

        self.cells = [[0]*16 for _ in range(4)]  # 4 rows, 16 columns

        self.create_grid()

    def create_grid(self):
        self.indicators = []
        for i in range(4):
            self.combo = ttk.Combobox(state="readonly", textvariable="wewe",values=["Drumkit", "Note", "Sound effects", "Synth"], width="3")
            self.combo.bind("<<ComboboxSelected>>", self.selection_changed)
            self.combo.place(x=5, y=79)

            # Add button for instrument selection
            self.combo1 = ttk.Combobox(state="readonly", textvariable="wewe",values=["Drumkit", "Note", "Sound effects", "Synth"], width="3")
            self.combo1.bind("<<ComboboxSelected>>", self.selection_changed)
            self.combo1.place(x=5, y=117)

            # Add button for instrument selection
            self.combo2 = ttk.Combobox(state="readonly", textvariable="wewe",values=["Drumkit", "Note", "Sound effects", "Synth"], width="3")
            self.combo2.bind("<<ComboboxSelected>>", self.selection_changed)
            self.combo2.place(x=5, y=155)

            # Add button for instrument selection
            self.combo3 = ttk.Combobox(state="readonly", textvariable="wewe",values=["Drumkit", "Note", "Sound effects", "Synth"], width="3")
            self.combo3.bind("<<ComboboxSelected>>", self.selection_changed)
            self.combo3.place(x=5, y=193)

            indicator_row = []
            for j in range(16):
                color = "grey" if (j // 4) % 2 == 0 else "#843942"
                sound_path = f"instrument{i+1}.wav"  # Replace with your sound file paths
                cell = CustomButton(self.master, width=14, height=20, bg_color=color,
                                    toggle_color="orange", toggle_command=lambda i=i, j=j: self.toggle_cell(i, j),
                                    sound_path=sound_path)
                cell.grid(row=i+1, column=j+1, padx=0, pady=8)
                self.cells[i][j] = (cell, color)  # Storing cell and original color

                indicator = tk.Canvas(self.master, width=6, height=6, bg="#794138")  # Set initial color to red
                indicator.grid(row=i+2, column=j+1, padx=0, pady=2)
                indicator_row.append(indicator)
            self.indicators.append(indicator_row)

    def toggle_cell(self, row, col):
        cell, original_color = self.cells[row][col]
        if cell.bg_color == original_color:
            cell.configure(bg="orange")  # Activated color
            cell.bg_color = "orange"
        else:
            cell.configure(bg=original_color)  # Deactivated color
            cell.bg_color = original_color

    def toggle_play(self):
        if self.playing:
            self.stop_playing()
        else:
            self.playing = True
            self.play_button.config(text="Stop")
            self.animate_indicators()

    def stop_playing(self):
        self.playing = False
        self.play_button.config(text="Play")

    def animate_indicators(self):
        for col in range(16):
            for row in range(4):
                if self.cells[row][col][0].bg_color == "orange":
                    pygame.mixer.Sound(self.cells[row][col][0].sound_path).play()
                self.indicators[row][col].configure(bg="#ed6140")
                self.master.update_idletasks()
            self.master.after(200)  # Adjust speed as needed
            for row in range(4):
                self.indicators[row][col].configure(bg="#794138")
        self.stop_playing()



def main():
    root = tk.Tk()
    app = LoopMakerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
