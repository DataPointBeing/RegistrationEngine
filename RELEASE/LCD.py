import serial


class LCD:
    def __init__(self, port):
        self._ser = serial.Serial(port)

    def write(self, content):
        self._ser.write(content.encode('UTF-8'))

    def backlight(self, value=True):
        if value:
            self._ser.write(b'\xfe\x42\x00') # may need to remove arg?
        else:
            self._ser.write(b'\xfe\x46')

    def brightness(self, intensity):
        self._ser.write(b'\xfe\x99' + intensity.to_bytes(1, "little"))

    def color(self, r, g, b):
        self._ser.write(b'\xfe\xd0' + r.to_bytes(1, "little") + g.to_bytes(1, "little") + b.to_bytes(1, "little"))

    def clear(self):
        self._ser.write(b'\xfe\x58')

    def backspace(self):
        self._ser.write(b'\x08')

    def cursor(self, style=""):
        if style == "underline":
            self._ser.write(b'\xfe\x54')
            self._ser.write(b'\xfe\x4A')
        elif style == "block":
            self._ser.write(b'\xfe\x4B')
            self._ser.write(b'\xfe\x53')
        else:
            self._ser.write(b'\xfe\x54')
            self._ser.write(b'\xfe\x4B')
