from Printer import Printer


class ReceiptProcessor:
    def __init__(self, printer):
        self._p = printer

        self.line_replace = {
            ("<image>", self.image),
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
        self._p.print_barcode(code, protocol)

    def image(self, path, _=0):
        self._p.print_image("Assets/Images/" + path, True)

    def spaced_on(self):
        self._p.set_line_height(50)

    def spaced_off(self):
        self._p.set_line_height()

    def justify_center(self):
        self._p.justify('C')

    def justify_right(self):
        self._p.justify('R')

    def justify_left(self):
        self._p.justify('L')

    def size_medium(self):
        self._p.set_size('M')

    def size_large(self):
        self._p.set_size('L')

    def size_small(self):
        self._p.set_size('S')

    def double_height_on(self):
        self._p.double_height_on()

    def double_height_off(self):
        self._p.double_height_off()

    def double_width_on(self):
        self._p.double_width_on()

    def double_width_off(self):
        self._p.double_width_off()

    def bold_on(self):
        self._p.bold_on()

    def bold_off(self):
        self._p.bold_off()

    def underline_on(self):
        self._p.underline_on()

    def underline_thick(self):
        self._p.underline_on(weight=2)

    def underline_off(self):
        self._p.underline_off()

    def invert_on(self):
        self._p.inverse_on()

    def invert_off(self):
        self._p.inverse_off()

    def strike_on(self):
        self._p.strike_on()

    def strike_off(self):
        self._p.strike_off()

    def make_print(self, text):
        ls = list()
        ls.extend(text)
        return lambda *args: self._p.print(*ls)

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
                    for s in range(1, (len(split) * 2) - 1, 2):
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
