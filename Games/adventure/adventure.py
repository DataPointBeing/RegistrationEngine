import time

from Games.adventure.Room import Room, RoomReplacement, Interactable
from registration import Registration

done = False
reg = Registration.engine()

current_room = None

verb_names = {
    "A": "OPEN",
    "B": "CLOSE",
    "C": "LOOK AT",
    "D": "PICK UP",
    "E": "TURN ON",
    "F": "TURN OFF",
    "G": "EAT",
}

friendly_names = {
    "I": "EGGS",
    "J": "MILK",
    "K": "CHEESE",
    "L": "KEY",
    "M": "BOWL",
    "N": "PAN",
    "O": "WHISK",

    "P": "TO BEDROOM",
    "Q": "DOOR",
    "R": "OVEN",
    "S": "COUNTER",
    "T": "FRIDGE",

    "U": "CUPBOARD",
    "V": "BED",
    "W": "STOVETOP",
    "X": "SHELVES",
    "Y": "PLATE"
}

action_mappings = {
    "open": "A",
    "close": "B",
    "look": "C",
    "pick_up": "D",
    "turn_on": "E",
    "turn_off": "F",
    "eat": "G",
    "quit": "H",

    "eggs": "I",
    "milk": "J",
    "cheese": "K",
    "key": "L",
    "bowl": "M",
    "pan": "N",
    "whisk": "O",

    "bedroom_move": "P",
    "kitchen_move": "Q",
    "oven": "R",
    "counter": "S",
    "fridge": "T",

    "cupboard": "U",
    "bed": "V",
    "burner": "W",
    "shelves": "X",
    "plate": "Y"
}

current_scans = []


def am(thing):
    return action_mappings[thing]


def make_action_text():
    global current_scans
    if len(current_scans) == 0:
        return "SCAN SOMETHING!"

    action_text_result = "?????"
    noun_pos_1 = -1
    noun_pos_2 = -1
    verb_pos = -1
    for i in range(len(current_scans)):
        if current_scans[i] in verb_names.keys():
            if verb_pos == -1:
                verb_pos = i
            else:
                return action_text_result
        else:
            if noun_pos_1 == -1:
                noun_pos_1 = i
            else:
                noun_pos_2 = i

    if verb_pos == -1:
        # two nouns
        if noun_pos_2 == -1:
            line = friendly_names[current_scans[noun_pos_1]]
            return line
        else:
            line_1 = "Use " + friendly_names[current_scans[noun_pos_1]]
            while len(line_1) < 16:
                line_1 += " "
            line_2 = "with " + friendly_names[current_scans[noun_pos_2]]
            return line_1 + line_2
    else:
        # noun and verb
        if noun_pos_1 == -1:
            line = verb_names[current_scans[verb_pos]] + " what?"
            return line
        else:
            line_1 = verb_names[current_scans[verb_pos]] + " the"
            while len(line_1) < 16:
                line_1 += " "
            line_2 = friendly_names[current_scans[noun_pos_1]]
            return line_1 + line_2


def change_room(room):
    global current_room
    global current_scans
    if current_room is not None:
        current_room.exit()
    room.enter()
    current_scans = []
    current_room = room
    reg.clear_screen()
    reg.write_to_screen(make_action_text())


def change_room_command(room):
    def change():
        global current_room
        global current_scans
        if current_room is not None:
            current_room.exit()
        room.enter()
        current_scans = []
        current_room = room
        reg.clear_screen()
        reg.write_to_screen(make_action_text())

    return change


def print_command(rec):
    def do_print():
        reg.print_receipt(rec)

    return do_print


bedroom = Room(
    "test",
    [],
    [],
    print_command("TEST"),
    print_command("TEST2")
)

kitchen = Room(
    "test2",
    [],
    [],
    print_command("TEST3"),
    print_command("TEST4")
)

stove = Room(
    "test",
    [],
    [],
    print_command("TEST")
)

counter = Room(
    "test",
    [],
    [],
    print_command("TEST")
)

fridge = Room(
    "test",
    [],
    [],
    print_command("TEST")
)


# DOORS
bedroom.add_interactable(
    Interactable(
        am("kitchen_move"),
        "DOOR",
        [am("open")],
        change_room_command(kitchen)
    )
)

kitchen.add_interactable(
    Interactable(
        am("bedroom_move"),
        "DOOR",
        [am("open"), None],
        change_room_command(bedroom)
    )
)


change_room(bedroom)


def add_scan(bc, __):
    global current_scans
    current_scans.append(bc)


for bc_id in action_mappings.values():
    print(bc_id)
    reg.add_valid_barcode(bc_id, add_scan)

reg.clear_screen()
reg.write_to_screen(make_action_text())
while not done:
    reg.query_scanner(filter_digits=True)
    if am("quit") in current_scans:
        done = True
        reg.pop_drawer()
    else:
        reg.clear_screen()
        reg.write_to_screen(make_action_text())

        result = current_room.poll_interactions(current_scans)
        if not result and len(current_scans) == 2:
            time.sleep(1.5)
            reg.clear_screen()
            reg.write_to_screen("That didn't work")
            time.sleep(1.5)
        elif result:
            time.sleep(1.5)

        if len(current_scans) >= 2:
            current_scans = []
            reg.clear_screen()
            reg.write_to_screen(make_action_text())


time.sleep(3)
