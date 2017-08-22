import csv
import os
import sys
import tkMessageBox
from PIL import Image, ImageEnhance
import json

GARMENT_SKU = 0
DESIGN = 1
GARMENT_COLOUR = 2
PRINT_COLOUR = 3
PRINT_COLOUR_ALT = 4

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    # application_path = sys._MEIPASS
    run_path = os.path.abspath(os.path.dirname(sys.argv[0]))
else:
    run_path = os.path.dirname(os.path.abspath(__file__))


class Create:

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_directory = os.path.dirname(file_path)
        print(self.file_directory)

    def read_csv(self):
        data = []
        with(open(self.file_path, 'r')) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            reader.next()  # Discount header
            for row in reader:
                data.append(row)
        while (['', '', '', '', '']) in data:
            data.remove(['', '', '', '', ''])  # Remove blank entries
        return data

    def create_all(self):

        data = self.read_csv()
        defaults = self.read_defaults()

        for i in range(0, len(data)):

            print "{} of {}".format(i, len(data))
            cancel = False

            while True:
                row = data[i]

                garment = row[GARMENT_SKU]
                scale_x = defaults[garment]["ScaleX"]
                scale_y = defaults[garment]["ScaleY"]
                x_offset = defaults[garment]["XOffset"]
                y = defaults[garment]["Y"]

                image = self.process_image(row, size=(scale_x, scale_y), x=x_offset, y=y)

                if image is not None:
                    self.save_image(image, row)
                    break
                else:
                    retry = self.retry_image(row)
                if not retry:
                    cancel = True
                    break

            if cancel:
                break

    def process_image(self, row, size, x, y, preview=False):
        try:
            foreground = self.open_foreground(row, size)
            background = self.open_background(row)
        except IOError:
            if preview:
                self.show_error_dialog(row)
            return
        x += background.size[0] / 2 - foreground.size[0] / 2
        background.paste(foreground, (x, y), foreground)
        if preview:
            background = Image.composite(background, Image.new('RGB', background.size, 'white'), background)
        return background

    def open_foreground(self, row, size):
        design_prefix = row[DESIGN][:2]
        design_path = '{0}/{2}{3}{4}.png'.format(self.file_directory, design_prefix, row[DESIGN],
                                                 row[PRINT_COLOUR], row[PRINT_COLOUR_ALT])
        foreground = Image.open(design_path).convert('RGBA')
        foreground.putalpha(ImageEnhance.Brightness(foreground.split()[3]).enhance(0.989))
        try:
            foreground.thumbnail(size, Image.ANTIALIAS)
        except ValueError as ve:
            self.show_dialog("Error", ve.message)
            return
        return foreground

    @staticmethod
    def open_background(row):
        source_path = 'Source/{0}/{0}{1}.png'.format(
            row[GARMENT_SKU],
            row[GARMENT_COLOUR]).replace(' ', '')
        background = Image.open(source_path).convert('RGBA')
        return background

    def save_image(self, image, row):
        filename = '{0}-{1}-{2}.png'.format(
            row[GARMENT_COLOUR],
            row[PRINT_COLOUR],
            row[PRINT_COLOUR_ALT])
        filename = filename.replace(' ', '-').replace('-.', '.')
        path = '{0}/{1}/{2}'.format(self.file_directory, row[DESIGN], row[GARMENT_SKU])
        if not os.path.exists(path):
            os.makedirs(path)
        image.save('{0}/{1}'.format(path, filename))

    @staticmethod
    def read_defaults(garment=None):
        with open('./Source/defaults.json') as data_file:
            data = json.load(data_file)
            print data
            if garment is not None:
                return data[garment]
            return data

    def save_defaults(self, garment, values):
        defaults = self.read_defaults()
        defaults[garment]["ScaleX"] = values[0]
        defaults[garment]["ScaleY"] = values[1]
        defaults[garment]["XOffset"] = values[2]
        defaults[garment]["Y"] = values[3]
        with open('./Source/defaults.json', 'w') as data_file:
            json.dump(defaults, data_file, indent=4)

    @staticmethod
    def retry_image(row):
        return tkMessageBox.askretrycancel(
            "Error",
            "Error during row: {}".format(row) +
            "\nPlease check {}{}{}.png or {} {} image name".format(
                row[DESIGN],
                row[PRINT_COLOUR],
                row[PRINT_COLOUR_ALT],
                row[GARMENT_SKU],
                row[GARMENT_COLOUR]
            ) +
            "\n\n(.PNG files must be in the same directory as data set CSV)")

    @staticmethod
    def show_error_dialog(self, row):
        self.show_dialog("Error",
                         "Error during row: {}".format(row) +
                         "\nPlease check {}{}{}.png or {} {} image name".format(
                             row[DESIGN],
                             row[PRINT_COLOUR],
                             row[PRINT_COLOUR_ALT],
                             row[GARMENT_SKU],
                             row[GARMENT_COLOUR]
                         ) + "\n\n(.PNG files must be in the same directory as data set CSV)")

    @staticmethod
    def show_dialog(title, message):
        tkMessageBox.showinfo(title, message)
