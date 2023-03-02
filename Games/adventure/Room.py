import io

from PIL import Image

from registration import Registration

reg = Registration.engine()

room_interactions = []


class Room:
    def __init__(self,
                 image,
                 interactables,
                 replacements,
                 first_text_generator=None,
                 next_text_generator=None,
                 exit_text_generator=None,
                 bits_size=0,
                 save_to_bits=None,
                 load_from_bits=None):
        self._image_name = "Assets/Images/" + image + ".png"
        img_bytes = io.BytesIO()
        img = Image.open(self._image_name)
        img.save(img_bytes, "PNG")
        self._image = img_bytes

        self._interactables = interactables
        self._replacements = replacements

        self._first_text_generator = first_text_generator
        self._next_text_generator = next_text_generator
        self._exit_text_generator = exit_text_generator
        self._bits_size = bits_size
        self._save_to_bits = save_to_bits
        self._load_from_bits = load_from_bits

        self._entered_before = False

    def enter(self, do_text=True):
        if do_text:
            if not self._entered_before and self._first_text_generator is not None:
                self._first_text_generator()
            elif self._next_text_generator is not None:
                self._next_text_generator()

        self.draw_room()
        self._entered_before = True

    def exit(self, do_text=True):
        if do_text and self._exit_text_generator is not None:
            self._exit_text_generator()

    def entered_before(self):
        return self._entered_before

    def draw_room(self):
        self.check_replacements()
        reg.print_image(self._image)

    def save_bits_size(self):
        return self._bits_size

    def get_interactables(self):
        return self._interactables

    def interactable_with_id(self, inter_id):
        for inter in self._interactables:
            if inter.get_id() == inter_id:
                return inter
        return None

    def interactables_with_id(self, inter_id):
        result = []
        for inter in self._interactables:
            if inter.get_id() == inter_id:
                result.append(inter)
        return result

    def add_interactable(self, inter):
        self._interactables.append(inter)

    def add_interactables(self, inters):
        for inter in inters:
            self._interactables.append(inter)

    def remove_interactables_with_id(self, inter_id):
        for inter in self._interactables:
            if inter.get_id() == inter_id:
                self._interactables.remove(inter)

    def replacement_with_id(self, repl_id):
        for repl in self._replacements:
            if repl.get_id() == repl_id:
                return repl
        return None

    def save(self):
        if self._save_to_bits is None:
            return None
        return self._save_to_bits()

    def load(self, bits):
        if self._load_from_bits is None:
            return None
        return self._load_from_bits(bits)

    def check_replacements(self):
        for rep in self._replacements:
            self._image = rep.try_replace(self._image)

    def poll_interactions(self, action_set):
        for inter in self._interactables:
            if inter.poll(action_set):
                return True
        return False


class Inventory:
    def __init__(self, interactables):
        self._interactables = interactables

    def interactable_with_id(self, inter_id):
        for inter in self._interactables:
            if inter.get_id() == inter_id:
                return inter
        return None

    def interactables_with_id(self, inter_id):
        result = []
        for inter in self._interactables:
            if inter.get_id() == inter_id:
                result.append(inter)
        return result

    def add_interactable(self, inter):
        self._interactables.append(inter)

    def add_interactables(self, inters):
        for inter in inters:
            self._interactables.append(inter)

    def remove_interactables_with_id(self, inter_id):
        for inter in self._interactables:
            if inter.get_id() == inter_id:
                self._interactables.remove(inter)

    def poll_interactions(self, action_set):
        for inter in self._interactables:
            if inter.poll(action_set):
                return True
        return False


class Interactable:
    def __init__(self,
                 inter_id,
                 action_set,
                 on_interact):
        self._inter_id = inter_id
        self._action_set = action_set
        self._action_set.append(inter_id)
        self._on_interact = on_interact

    def get_id(self):
        return self._inter_id

    def poll(self, action_set):
        a_s = action_set.copy()
        if len(a_s) == 1:
            a_s.append(None)

        if "ANY" in self._action_set and self._inter_id in a_s:
            pass
        elif self._inter_id not in action_set or (len(action_set) > 1 and action_set[0] == action_set[1]):
            return False
        else:
            for action in a_s:
                if action != self._inter_id and action not in self._action_set:
                    return False

        return self._on_interact()


class RoomReplacement:
    def __init__(self,
                 repl_id,
                 location,
                 image,
                 condition,
                 on_replacement=None):
        self._repl_id = repl_id
        self._location = location
        self._image = "Assets/Images/" + image + ".png"
        self._condition = condition
        self._on_replacement = on_replacement
        self._triggered = False

    def get_id(self):
        return self._repl_id

    def re_enable(self):
        self._triggered = False

    def try_replace(self, img):
        if not self._triggered and self._condition():
            img.seek(0)
            img_loaded = Image.open(img)
            repl_loaded = Image.open(self._image)
            img_loaded.paste(repl_loaded, self._location, repl_loaded)
            img = io.BytesIO()
            img_loaded.save(img, "PNG")
            if self._on_replacement is not None:
                self._on_replacement()
            self._triggered = True
        return img
