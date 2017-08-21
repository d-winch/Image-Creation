from tkinter import Tk, Label, Button, Entry, W, END, Toplevel
from tkFileDialog import askopenfilename
import tkMessageBox
import individualGUI
import creation
import sys
import os


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class GUI:
    def __init__(self, master):
        self.master = master
        root.iconbitmap(default=resource_path("icon.ico"))
        master.protocol("WM_DELETE_WINDOW", root.destroy)
        master.title("Image Creation")

        self.label_file = Label(master, text="Enter File Path...")
        self.button_browse = Button(master, text="Browse...", command=self.browse_file)
        self.button_indv = Button(master, text="Create Individual", command=self.individual)
        self.button_close = Button(master, text="Create All", command=self.create_all)

        self.entry_file = Entry(master, text="Set path")
        self.label_file.grid(row=0, column=0, sticky=W)
        self.entry_file.grid(row=1, column=0)
        self.button_browse.grid(row=1, column=2)
        self.button_indv.grid(row=2, column=0, sticky=W)
        self.button_close.grid(row=2, column=2)

        for child in master.winfo_children():
            child.grid_configure(padx=10, pady=5)

    def browse_file(self):
        f = askopenfilename()
        self.entry_file.delete(0, END)
        self.entry_file.insert(END, f)

    def individual(self):
        if self.entry_file.get() is '':
            self.show_dialog(title="File Missing", message="Please enter a file path and try again...")
            return
        ind_master = Toplevel()
        gui_ind = individualGUI.IndividualGUI(ind_master, self.entry_file.get())
        ind_master.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(ind_master))
        self.master.withdraw()
        gui_ind.show()

    def on_closing(self, ind_master):
        print("HERE")
        self.master.deiconify()
        ind_master.destroy()

    def create_all(self):
        if self.entry_file.get() is '':
            self.show_dialog(title="File Missing", message="Please enter a file path and try again...")
            return
        c = creation.Create(self.entry_file.get())
        c.create_all()

    @staticmethod
    def show_dialog(title, message):
        tkMessageBox.showinfo(title, message)

root = Tk()
my_gui = GUI(root)
root.mainloop()
