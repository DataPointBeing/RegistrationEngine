import re
import threading
import time

from pynput.keyboard import Key, Listener

from Printer import Printer
from Drawer import Drawer
from LCD import LCD
from ReceiptProcessor import ReceiptProcessor

LCD_PORT = 0
PRINTER_PORT = 0


class Registration:
    """
    REGISTRATION ENGINE

    Instantiate this at the start of your game and access the below functions to
    interface with your register hardware.

    ------------------

    Requires:
    LCD.py, for instructing a 32-character LCD.
    Printer.py, for instructing a thermal receipt printer.
    Drawer.py, for instructing a cash register drawer to pop open.
    ReceiptProcessor.py, for processing formatted text files into printable receipts.

    RELEASE contains versions of the above meant for interacting with actual hardware,
    while TESTING contains versions that run without hardware and approximate output
    on the system for making and testing games in a platform-agnostic workflow. Read
    the information in those files to understand their behavior.
    """

    _reg = None

    @staticmethod
    def engine():
        if Registration._reg is None:
            Registration._reg = Registration(LCD_PORT, PRINTER_PORT)
        return Registration._reg

    def __init__(self, lcd_port, printer_port):
        """
        Engine constructor.

        :param lcd_port: the USB port for our LCD (value doesn't matter on TESTING LCD.py)
        :param printer_port: the USB port for our printer (value doesn't matter on TESTING Printer.py)
        """
        self._printer = Printer()
        # self._printer.USB.write(self._printer.getPrintData().getvalue())

        self._lcd = LCD(lcd_port)

        self._querying = False

        self._lcd_lock = threading.Condition()

        self._idle = None

        self._rec_proc = ReceiptProcessor(self._printer)

        self._drawer = Drawer()

        self._valid_barcodes = []

    def add_valid_barcode(self, bc, func, partial=False):
        """
        Add a new barcode that can be recognized by the system.

        :param bc: The text content of the barcode.

        :param func: The function to run when this code is scanned...
        The function should adhere to to the following signature:

        def example(whole, extension):
            ... do things here

        whole will be supplied with the *entire* barcode string that was scanned,
        and extension will just be the substring that follows bc. (As such, this
        will always be an empty string when partial = False.)

        :param partial: Whether to require an exact barcode text match; if True,
        bc should be the start of a barcode, as any code *starting* with bc will
        be recognized. If False, bc should be an exact match.
        """
        self._valid_barcodes.append((bc, func, partial))

    def remove_valid_barcode(self, bc):
        """
        Forget a recognized barcode marked by the given string.

        :param bc: the barcode string to remove.
        """
        for i in range(len(self._valid_barcodes)):
            if self._valid_barcodes[i][0] == bc:
                del self._valid_barcodes[i]
                return

    def pop_drawer(self):
        """
        Ding! Pop open the drawer.
        (on all of our prototypes, this just plays a sound.)
        """
        self._drawer.pop()

    def get_lcd(self):
        """
        Get the in-between for talking to our character LCD.

        :return: the LCD object.
        """
        return self._lcd

    def get_printer(self):
        """
        Get the in-between for talking to our thermal printer.

        :return: the Printer object.
        """
        return self._printer

    def set_idle_animation(self, fps=None, frames=None):
        """
        Set up an idle animation to display on the character LCD on loop when
        no prompt is displayed. See the IdleAnimation class below.

        :param fps: the (approximate) animation speed in frames/second.
        :param frames: the list of strings to use as frames. Should be 32 characters;
        the first 16 will occupy the top line, the remaining the bottom.
        """
        self._lcd.clear()

        if self._idle is not None:
            self._idle.end()

        if fps is not None and frames is not None:
            self._idle = IdleAnimation(fps, frames, self._lcd, self._lcd_lock)
            threading.Thread(target=self._idle.run).start()

    def set_proc_idle_animation(self, fps=None, procedure=None):
        """
        Set up a procedural idle animation to display on the character LCD on loop when
        no prompt is displayed. See the ProceduralIdleAnimation class below.

        :param fps: the (approximate) animation speed in frames/second.
        :param procedure: a function generating the display content each frame.

        It should adhere to the following signature:

        def example(frame_number):
            ... do something
            return frame_string  # Ideally 32 characters in length!

        where frame_number is what number this frame is (from creation of this animation).
        """
        self._lcd.clear()

        if self._idle is not None:
            self._idle.end()

        if fps is not None and procedure is not None:
            self._idle = ProceduralIdleAnimation(fps, procedure, self._lcd, self._lcd_lock)
            threading.Thread(target=self._idle.run).start()

    def stop_idle_animation(self):
        """
        Halt and remove the currently-running idle animation.
        """
        if self._idle is not None:
            self._idle.end()

    def write_to_screen(self, content):
        """
        Write text content directly to the character LCD.
        *** Remember that idle animations will overwrite your text, so halt them if needed!

        :param content: the text to write.
        """
        self._lcd.write(content)

    def clear_screen(self):
        """
        Delete all text content on the character LCD.
        *** Remember that idle animations will overwrite this, so halt them if needed!
        """
        self._lcd.clear()

    def query_scanner(self, prompt=None, filter_digits=False):
        """
        Awaits a (recognized) scanned barcode. When one is received, its corresponding
        function is run immediately.

        Remember, the thread this is called on will halt until it receives valid scanner input!
        It is STRONGLY recommended not to await multiple queries on different threads at the same time.

        :param prompt: (optional) a text prompt to display on the LCD while waiting.
        :param filter_digits: whether to remove all digits 0-9 from a barcode when processing it.
        :return: the return value of the barcode's function.
        """
        do_prompt = prompt is not None

        if do_prompt:
            self._querying = True
            self._lcd_lock.acquire()
            self._lcd.clear()
            self._lcd.write(prompt)
            self._lcd.next_line()

        x = input()
        res = self.valid_barcode(x, filter_digits)

        while res is None:
            if do_prompt:
                self._lcd.clear()
                self._lcd.write(prompt)
                self._lcd.next_line()
            x = input()
            res = self.valid_barcode(x, filter_digits)

        if do_prompt:
            self._lcd_lock.release()
            self._querying = False

        return res[1](res[0], x[len(res[0]):])

    def valid_barcode(self, bc, filter_digits=False):
        """
        Retrieves the valid barcode tuple for given barcode string, if one's been registered.
        This is a tuple in the following format -- (barcode_string, function, partial) --
        where barcode_string is the text content to match, function is the code to run when scanned,
        and partial is whether a full match is needed or barcode_string is just a code's start.

        :param bc: barcode string to search for a valid match for.
        :param filter_digits: whether to remove all digits 0-9 from bc before searching.
        :return: the valid barcode tuple, if one exists for bc.
        """

        scanned = bc
        if filter_digits:
            scanned = re.sub(r'[0-9]', '', scanned)
        for code in self._valid_barcodes:
            code_len = len(code[0])
            if len(scanned) >= code_len and (len(scanned) == code_len or code[2]) and scanned[:code_len] == code[0]:
                return code
        return None

    def query_keypad(self, prompt, response_max_length=16, match_length=False):
        """
        Awaits a valid numeric passcode from the keypad. Input is handled manually rather than through
        Python's input() call (so that the LCD can update as you type).

        Remember, the thread this is called on will halt until it receives valid input!
        It is STRONGLY recommended not to await multiple queries on different threads at the same time.

        :param prompt: (optional) a text prompt to display on the LCD while waiting.
        :param response_max_length: the maximum response length to allow.
        :param match_length: whether to force the response to MATCH response_max_length.
        :return: the number input by the user.
        """
        self._querying = True
        self._lcd_lock.acquire()

        self._lcd.clear()
        self._lcd.write(prompt)
        self._lcd.next_line()

        x = self._keypad_read_live(response_max_length)

        while re.search('[^0-9]', x) or (match_length and not len(x) == response_max_length):
            self._lcd.clear()
            self._lcd.write(prompt)
            self._lcd.next_line()
            x = self._keypad_read_live(response_max_length)

        self._lcd_lock.release()
        self._querying = False
        return x

    def _keypad_read_live(self, max_len):
        """
        Helper function for keypad reading. Uses a thread.

        :param max_len: maximum length.
        :return: a full numeric string constructed from key inputs.
        """
        result = ""
        last_pressed = [time.time()] * 10
        read = None

        def _read_keys(k):
            nonlocal result
            nonlocal last_pressed
            nonlocal read
            read = k

            as_char = read.char if hasattr(read, "char") else None
            if as_char is not None and as_char.isdigit():
                as_int = int(as_char)
                now = time.time()
                if now - last_pressed[as_int] > 0.05 and len(result) < max_len:
                    result += as_char
                    self._lcd.write(as_char)
                last_pressed[as_int] = time.time()
            elif read == Key.enter:
                self._lcd.clear()
                return False
            elif read == Key.backspace and len(result) > 0:
                result = result[:-1]
                self._lcd.backspace()

        with Listener(on_press=_read_keys) as listener:
            listener.join()

        return result

    def print_receipt(self, path, replacements=None):
        """
        Prints a receipt from a pre-made text file.
        Formatting is handled via ReceiptProcessor.py, see there for more details.

        :param path: filename (minus extension) in the Assets/Text directory.
        :param replacements: a list of replacements for the text content.
        These are in the form of a tuple -- (original_text, replacement_text).
        """
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
        """
        Prints a receipt from a list of lines.
        Formatting is handled via ReceiptProcessor.py, see there for more details.

        :param lines: set of lines to print.
        """
        instructions_per_line = self._rec_proc.make_print_instructions(lines)

        self._printer.set_default()
        self._printer.feed()

        for line in instructions_per_line:
            for i in line:
                i()
                self._printer.feed()

        self._printer.feed()

    def print_image(self, image):
        """
        Prints an image by name from Assets/Images, or direct from a file-like object.

        :param image: the file-like object to print, or a PNG name (sans .png).
        """
        im = image
        if isinstance(im, str):
            im = "Assets/Images/" + im + ".png"
        self._printer.print_image(im)



class IdleAnimation:
    """
    Class for asynchronous LCD idle animations.
    """

    def __init__(self, fps, frames, lcd, cond):
        self._framerate = fps
        self._animation = frames

        self._current_frame = -1
        self._finished = False

        self._lcd = lcd

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
    """
    Class for *procedural* asynchronous LCD idle animations.
    """

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
