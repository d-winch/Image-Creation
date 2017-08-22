from tkinter import *
import os
import csv
import json
import creation


class IndividualGUI:

    def __init__(self, master, file_path):

        self.master = master
        self.file_path = file_path
        self.file_directory = os.path.dirname(file_path)
        print(self.file_directory)
        self.creation = creation.Create(file_path)
        self.data = self.creation.read_csv()

        master.title("Image Creation")

        self.label_code = Label(master, text="Design Code")
        self.label_garment = Label(master, text="Garment")
        self.label_scale = Label(master, text="Scale (X Y)")
        self.label_coords = Label(master, text="Co-ords (X Y)")

        self.entry_code = Entry(master, textvariable=StringVar(master))
        self.entry_scalex = Entry(master, textvariable=StringVar(master, "Scale X"))
        self.entry_scaley = Entry(master, textvariable=StringVar(master, "Scale Y"))
        self.entry_coordsx = Entry(master, textvariable=StringVar(master, "X Offset"))
        self.entry_coordsy = Entry(master, textvariable=StringVar(master, "Y"))
        self.entry_scalex.bind('<FocusIn>', self.on_entry_click)
        self.entry_scaley.bind('<FocusIn>', self.on_entry_click)
        self.entry_coordsx.bind('<FocusIn>', self.on_entry_click)
        self.entry_coordsy.bind('<FocusIn>', self.on_entry_click)

        self.variable = StringVar(master)
        self.variable.set("Select a garment")  # default value
        self.variable.trace("w", self.option_changed)
        self.option_garment = OptionMenu(master, self.variable, *self.get_garments())

        self.button_save = Button(master, text="Save Defaults", command=self.save_defaults)
        self.frame = Frame(master)
        self.button_preview = Button(self.frame, text="Preview", command=self.preview)
        self.button_create = Button(self.frame, text="Create All", command=self.create)

        self.label_code.grid(row=0, column=0, sticky=W)
        self.label_garment.grid(row=1, column=0, sticky=W)
        self.label_scale.grid(row=2, column=0, sticky=W)
        self.label_coords.grid(row=3, column=0, sticky=W)

        self.entry_code.grid(row=0, column=1)
        self.entry_scalex.grid(row=2, column=1)
        self.entry_scaley.grid(row=2, column=2)
        self.entry_coordsx.grid(row=3, column=1)
        self.entry_coordsy.grid(row=3, column=2)

        self.option_garment.grid(row=1, column=1, columnspan=2, sticky=E+W)

        self.button_save.grid(row=4, column=0)
        self.button_preview.pack(side="left", padx=10, pady=5)
        self.button_create.pack(side="right", padx=10, pady=5)
        self.frame.grid(row=4, column=2)

        for child in master.winfo_children():
            if not isinstance(child, Frame):
                child.grid_configure(padx=10, pady=5)

    def read_csv(self):
        with(open(self.file_path, 'r')) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            reader.next()
            data = list(reader)
        return data

    def show(self):
        self.master.mainloop()

    def preview(self):
        print("Preview")
        code = self.get_rows()
        if code is None:
            return
        try:
            image_preview = self.get_image(code[0], is_preview=True)
            image_preview.show()
        except ValueError:
            self.creation.show_dialog("Error", 'Must be an integer value (e.g., 100)\nand cannot be blank')
        except AttributeError:
            print("image_preview.show() run after process_image() encountered error and returned None")

    def get_image(self, code, is_preview=False):
        image = self.creation.process_image(
            code,
            size=(int(self.entry_scalex.get()), int(self.entry_scaley.get())),
            x=int(self.entry_coordsx.get()),
            y=int(self.entry_coordsy.get()),
            preview=is_preview
        )
        return image

    def create(self):
        print("Create")
        codes = self.get_rows()
        if codes is None:
            return
        for code in codes:
            try:
                image = self.get_image(code)
                self.creation.save_image(image, code)
            except ValueError:
                self.creation.show_dialog("Error", 'Must be an integer value (e.g., 100)\nand cannot be blank')
            except AttributeError:
                print("Tried to save when image process_error() encountered error and returned None")
                return

    # Return data rows from selection
    def get_rows(self):
        codes = []
        garment = self.variable.get()
        for i, j, k, l, m in self.data:
            if (i, j) == (garment, self.entry_code.get()):
                codes.append([i, j, k, l, m])
        if len(codes) == 0:
            self.creation.show_dialog(
                "Error",
                "File does not include this combination as a variation\nPlease check your entries.")
            return
        return codes

    @staticmethod
    def get_garments():
        with open('./Source/defaults.json') as data_file:
            data = json.load(data_file)
        garments = data.keys()
        garments.sort()
        return garments

    def option_changed(self, *args):
        print args
        print "the user chose the value {}".format(self.variable.get())
        option = self.variable.get()
        # Returns the default ScaleX, ScaleY, and default co-ordinates X, Y (X is an offset from center)
        g = self.creation.read_defaults(option)

        self.entry_scalex.delete(0, END)
        self.entry_scaley.delete(0, END)
        self.entry_coordsx.delete(0, END)
        self.entry_coordsy.delete(0, END)

        self.entry_scalex.insert(0, g["ScaleX"])
        self.entry_scaley.insert(0, g["ScaleY"])
        self.entry_coordsx.insert(0, g["XOffset"])
        self.entry_coordsy.insert(0, g["Y"])

    @staticmethod
    def on_entry_click(event):
        if not event.widget.get().lstrip("-").isdigit():
            event.widget.delete(0, END)

    def save_defaults(self):
        garment = self.variable.get()
        try:
            values = (int(self.entry_scalex.get()),
                      int(self.entry_scaley.get()),
                      int(self.entry_coordsx.get()),
                      int(self.entry_coordsy.get()))
        except ValueError:
            self.creation.show_dialog("Error", 'Must be an integer value (e.g., 100)\nand cannot be blank')
            return
        self.creation.save_defaults(garment, values)
        self.creation.show_dialog("Success", "Default values saved for " + garment)
