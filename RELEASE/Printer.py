import io

import usb.core
import time
import sys
import math


class Printer:

    def __init__(self):
        pass

    # Reset text formatting parameters.
    def set_default(self):
        self.justify('L')
        self.inverse_off()
        self.double_height_off()
        self.set_line_height(30)
        self.bold_off()
        self.underline_off()
        self.set_barcode_height(50)
        self.set_size('s')

    def set_barcode_height(self, val=50):
        pass

    def print_barcode(self, text, type):
        pass

    def normal(self):
        pass

    def inverse_on(self):
        pass

    def inverse_off(self):
        pass

    def upside_down_on(self):
        pass

    def upside_down_off(self):
        pass

    def double_height_on(self):
        pass

    def double_height_off(self):
        pass

    def double_width_on(self):
        pass

    def double_width_off(self):
        pass

    def strike_on(self):
        pass

    def strike_off(self):
        pass

    def bold_on(self):
        pass

    def bold_off(self):
        pass

    def justify(self, value):
        c = value.upper()
        if c == 'C':
            pass
        elif c == 'R':
            pass
        else:
            pass

    # Feeds by the specified number of lines
    def feed(self, x=1):
        pass

    def set_size(self, value):
        c = value.upper()
        if c == 'L':  # Large: double width and height
            pass
        elif c == 'M':  # Medium: double height
            pass
        else:  # Small: standard width and height
            pass

    # Underlines of different weights can be produced:
    # 0 - no underline
    # 1 - normal underline
    # 2 - thick underline
    def underline_on(self, weight=1):
        if weight > 2: weight = 2


    def underline_off(self):
        pass

    def print_image(self, image_file):
        pass

    def set_line_height(self, val=32):
        if val < 24: val = 24
        self.lineSpacing = val - 24

    # Copied from Arduino lib for parity; may not work on all printers
    def set_char_spacing(self, spacing):
        pass

    # Overloading print() in Python pre-3.0 is dirty pool,
    # but these are here to provide more direct compatibility
    # with existing code written for the Arduino library.
    def print(self, *args):
        for arg in args:
            pass

    # For Arduino code compatibility again
    def println(self, *args):
        for arg in args:
            pass
        pass
