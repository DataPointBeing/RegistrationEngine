import simpleaudio as sa


class Drawer:
    def __init__(self):
        self._wave_object = sa.WaveObject.from_wave_file('Assets/register.wav')

    def pop(self):
        self._wave_object.play()
