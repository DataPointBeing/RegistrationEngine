import serial


class LCD:
    def __init__(self, port):
        self._backlit = False
        self._data = ""

    def _print_data(self):
        for i in range(0, 5):
            print()
        print("LCD (backlight " + ("on" if self._backlit else "off") + "):")
        print(self._data[:16])
        print(self._data[16:])

    def write(self, content):
        self._data += content
        while len(self._data) > 32:
            self._trim()
        self._print_data()

    def next_line(self):
        while len(self._data) % 16 > 0:
            self._data += " "
        self._trim()

    def _trim(self):
        self._data = self._data[16:]

    def backlight(self, value=True):
        self._backlit = value

    def brightness(self, intensity):
        pass

    def color(self, r, g, b):
        pass

    def clear(self):
        self._data = ""
        self._print_data()

    def backspace(self):
        if len(self._data) >= 1:
            self._data = self._data[:-1]
        self._print_data()

    def cursor(self, style=""):
        pass
