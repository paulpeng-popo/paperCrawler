"""
show all JPG files in DataSetPath and let user to rename them as well resize them with 100x30
"""

import os
import tkinter as tk
from tkinter import messagebox

from config import DataSetPath
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rename")
        self.geometry("300x200")
        self.resizable(False, False)
        self.files = os.listdir(DataSetPath)
        self.files = [os.path.join(DataSetPath, f)
                      for f in self.files if f.endswith(".jpg")]
        # filter out files that the name is not 6 characters
        self.files = [f for f in self.files if len(
            f.split(os.sep)[-1].split(".")[0]) == 6]

        self.index = 0
        self.label = tk.Label(self)
        self.label.pack()
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.button = tk.Button(self, text="Rename", command=self.rename)
        self.button.pack()
        self.next()

        # set enter key to rename
        self.bind("<Return>", lambda e: self.rename())

    def next(self):
        if self.index < len(self.files):
            print(len(self.files) - self.index)
            img = Image.open(self.files[self.index])
            img = img.resize((100, 30))
            img = ImageTk.PhotoImage(img)
            self.label.configure(image=img)
            self.label.image = img
            self.index += 1
        else:
            messagebox.showinfo("Info", "All done!")
            self.destroy()

    def rename(self):
        new_name = self.entry.get()
        if len(new_name) != 6:
            messagebox.showerror("Error", "The name must be 6 characters!")
            # set focus to back to main window
            self.focus()
            return

        if new_name:
            os.rename(self.files[self.index - 1],
                      os.path.join(DataSetPath, new_name + ".jpg"))
            self.entry.delete(0, tk.END)
            self.next()
        else:
            messagebox.showerror("Error", "Please enter a name!")


if __name__ == "__main__":
    app = App()
    app.mainloop()
