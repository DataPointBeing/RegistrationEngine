import os
import re
import threading
import time

from Adafruit_Thermal_USB import Printer
from Drawer import Drawer
from LCD import LCD


class IdleAnimation:
    def __init__(self, fps, frames, lcd, cond):
        self._framerate = fps
        self._animation = frames

        self._current_frame = -1
        self._finished = False

        self._condition = cond

    def end(self):
        self._finished = True

    def run(self):
        while not self._finished:
            self._condition.acquire()
            self._current_frame = (self._current_frame + 1) % len(self._animation)
            self._lcd.clear()
            self._lcd.write(self._animation[self._current_frame])
            self._condition.release()

            time.sleep(1 / self._framerate)


class ProceduralIdleAnimation:
    def __init__(self, fps, generator, lcd, cond):
        self._framerate = fps
        self._generator = generator

        self._current_frame = -1
        self._finished = False

        self._lcd = lcd
        self._condition = cond

    def end(self):
        self._finished = True

    def run(self):
        while not self._finished:
            self._condition.acquire()
            self._current_frame += 1
            self._lcd.clear()
            self._lcd.write(self._generator(self._current_frame))
            self._condition.release()

            time.sleep(1 / self._framerate)


class ReceiptProcessor:
    def __init__(self, printer):
        self._p = printer

        self.line_replace = {
            ("<image>", self.image),
            ("<image_small>", self.image_small),
            ("<barcode>", self.barcode),
        }
        self.multi_line_preprocess = {
            ("<spaced>", self.spaced_on, self.spaced_off),
            ("<right>", self.justify_right, self.justify_left),
            ("<center>", self.justify_center, self.justify_left),
            ("<large>", self.size_large, self.size_small),
            ("<medium>", self.size_medium, self.size_small),
            ("<tall>", self.double_height_on, self.double_height_off),
            ("<wide>", self.double_width_on, self.double_width_off),
            ("<b>", self.bold_on, self.bold_off)
        }
        self.line_process = {
            ("<u>", self.underline_on, self.underline_off),
            ("<i>", self.invert_on, self.invert_off),
            ("<s>", self.strike_on, self.strike_off),
        }

    def barcode(self, code, protocol=8):
        self._p.getPrintData().write(b'\x1D\x48\x30')
        self._p.getPrintData().write(b'\x1D\x68\x32')
        self._p.getPrintData().write(b'\x1D\x77\x02')
        self._p.getPrintData().write(b'\x1D\x6B\x08\x02')
        self._p.getPrintData().write(code.encode('cp437', 'ignore'))
        self._p.getPrintData().write(b'\x00\x00\x00\x00')

    def image(self, path, _=0):
        self._p.printImage("Assets/Images/" + path, True)

    def image_small(self, path, _=0):
        self._p.printImage("Assets/Images/" + path)

    def spaced_on(self):
        self._p.setLineHeight(50)

    def spaced_off(self):
        self._p.setLineHeight()

    def justify_center(self):
        self._p.justify('C')

    def justify_right(self):
        self._p.justify('R')

    def justify_left(self):
        self._p.justify('L')

    def size_medium(self):
        self._p.setSize('M')

    def size_large(self):
        self._p.setSize('L')

    def size_small(self):
        self._p.setSize('S')

    def double_height_on(self):
        self._p.doubleHeightOn()

    def double_height_off(self):
        self._p.doubleHeightOff()

    def double_width_on(self):
        self._p.doubleWidthOn()

    def double_width_off(self):
        self._p.doubleWidthOff()

    def bold_on(self):
        self._p.boldOn()

    def bold_off(self):
        self._p.boldOff()

    def underline_on(self):
        self._p.underlineOn()

    def underline_thick(self):
        self._p.underlineOn(weight=2)

    def underline_off(self):
        self._p.underlineOff()

    def invert_on(self):
        self._p.inverseOn()

    def invert_off(self):
        self._p.inverseOff()

    def strike_on(self):
        self._p.strikeOn()

    def strike_off(self):
        self._p.strikeOff()

    def make_print(self, text):
        l = list()
        l.extend(text)
        return lambda *args: self._p.print(*l)

    def make_print_instructions(self, lines):
        instructions = []
        ml_preprocess_found = [False] * len(self.multi_line_preprocess)
        for line in lines:
            ln = line
            line_start_inst = []
            line_end_inst = []

            # line asset load
            replace = self._check_replacements(ln)
            if replace is not None:
                instructions.append([replace])
                continue

            # multi-line preprocess
            i = 0
            for tag, before, after in self.multi_line_preprocess:
                split = ln.split(tag)
                if len(split) > 1:
                    if ml_preprocess_found[i]:
                        ml_preprocess_found[i] = False
                        line_end_inst.append(after)
                    else:
                        if len(split) > 2:
                            line_start_inst.append(before)
                            line_end_inst.append(after)
                        else:
                            ml_preprocess_found[i] = True
                            line_start_inst.append(before)
                    ln = "".join(split)
                i += 1

            # line process
            broken = [ln]
            for tag, before, after in self.line_process:
                next_broken = []
                seeking_match = False
                for piece in broken:
                    if type(piece) != str:
                        next_broken.append(piece)
                        continue
                    split = piece.split(tag)
                    for s in range(1, (len(split)*2)-1, 2):
                        split.insert(s, after if seeking_match else before)
                        seeking_match = not seeking_match
                    next_broken += split
                if seeking_match:
                    raise Exception("Opening " + tag + " was found, but no closing tag was found to match.")
                broken = next_broken

            for i in range(len(broken)):
                if type(broken[i]) == str:
                    if len(broken[i]) > 0:
                        broken[i] = self.make_print(broken[i])
                    else:
                        broken[i] = lambda: None

            instructions.append(line_start_inst + broken + line_end_inst)

        return instructions

    def _check_replacements(self, line):
        ln = line
        for tag, func in self.line_replace:
            split = ln.split(tag)
            if len(split) > 1:
                ln = "".join(split)
                args = ln.split("#")
                return lambda *foo: func(*args)
        return None


class Registration:
    def __init__(self, lcd_port):
        self._printer = Printer(9600)
        #self._printer.USB.write(self._printer.getPrintData().getvalue())

        self._lcd = LCD(lcd_port)

        self._querying = False

        self._lcd_lock = threading.Condition()

        self._idle = None

        self._rec_proc = ReceiptProcessor(self._printer)

        self._drawer = Drawer()

        self._valid_barcodes = []

    def add_valid_barcode(self, bc, func):
        self._valid_barcodes.append((bc, func))

    def remove_valid_barcode(self, bc):
        for i in range(len(self._valid_barcodes)):
            if self._valid_barcodes[i][0] == bc:
                del self._valid_barcodes[i]
                return

    def pop_drawer(self):
        self._drawer.pop()

    def get_lcd(self):
        return self._lcd

    def get_printer(self):
        return self._printer

    def set_idle_animation(self, fps=None, frames=None):
        self._lcd.clear()

        if self._idle is not None:
            self._idle.end()

        if fps is not None and frames is not None:
            self._idle = IdleAnimation(fps, frames, self._lcd, self._lcd_lock)
            threading.Thread(target=self._idle.run).start()

    def set_proc_idle_animation(self, fps=None, procedure=None):
        self._lcd.clear()

        if self._idle is not None:
            self._idle.end()

        if fps is not None and procedure is not None:
            self._idle = ProceduralIdleAnimation(fps, procedure, self._lcd, self._lcd_lock)
            threading.Thread(target=self._idle.run).start()

    def query_scanner(self, prompt=None):
        self._querying = True

        os.system('cls')
        if prompt is not None: print(prompt)
        x = input()
        res = self.valid_barcode(x)

        while res is None:
            os.system('cls')
            if prompt is not None: print(prompt)
            x = input()
            res = self.valid_barcode(x)

        self._querying = False
        return res[1](res[0])

    def valid_barcode(self, bc):
        for code in self._valid_barcodes:
            if bc == code[0]:
                return code
        return None

    def query_keypad(self, prompt, response_max_length, match_length=False):
        self._querying = True

        os.system('cls')
        print(prompt)
        x = input()[:response_max_length]

        while re.search('[^0-9]', x) or (match_length and not len(x) == response_max_length):
            os.system('cls')
            print(prompt)
            x = input()[:response_max_length]

        self._querying = False
        return x

    def print_receipt(self, path, replacements=None):
        my_file = open("Assets/Text/" + path + ".txt", "r")
        data = my_file.read()

        lines = data.split("\n")
        my_file.close()

        if replacements is not None:
            for line_no in range(len(lines)):
                for rep in replacements:
                    lines[line_no] = lines[line_no].replace(rep[0], rep[1])

        self.print_receipt_manual(lines)

    def print_receipt_manual(self, lines):
        instructions_per_line = self._rec_proc.make_print_instructions(lines)
        #print(instructions_per_line)

        self._printer.setDefault()
        self._printer.feed()
        #self._printer.getPrintData().seek(0)
        #self._printer.getPrintData().truncate(0)
        for line in instructions_per_line:
            for i in line:
                i()
                self._printer.feed()

        self._printer.feed()

        #print("ok:" + self._printer.getPrintData().getvalue().decode("CP437"))
        #print("b:" + str(self._printer.getPrintData().getvalue()))
        #self._printer.USB.write(self._printer.getPrintData().getvalue())
