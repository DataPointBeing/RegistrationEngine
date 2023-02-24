import serial


class LCD:
    def __init__(self, port):
        self._backlit = False

        self._data = ""
        self._cursor = 1

    def _print_data(self):
        print("LCD (backlight " + "on" if self._backlit else "off" + "):")
        for i in range(0, 80):
            print()
        print(self._data[:16])
        print(self._data[16:])

    def write(self, content):
        self._data += content
        self._cursor += len(content)
        while len(self._data) > 32:
            self._data = self._data[16:]
            self._cursor -= 16
        self._print_data()

    def backlight(self, value=True):
        self._backlit = value

    def brightness(self, intensity):
        pass

    def color(self, r, g, b):
        pass

    def clear(self):
        self._data = ""
        self._cursor = 1
        self._print_data()

    def splash(self, content):
        pass

    def backspace(self):
        if len(self._data) >= 1:
            self._data = self._data[:-1]
            self._cursor -= 1

    def cursor(self, style=""):
        pass
