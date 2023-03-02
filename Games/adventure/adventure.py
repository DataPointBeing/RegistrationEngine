import time

from Games.adventure.Room import Room, RoomReplacement, Interactable, Inventory
from registration import Registration

done = False
won = False
reg = Registration.engine()

current_room = None

verb_names = {
    "aA": "OPEN",
    # "aB": "CLOSE",
    "aC": "LOOK AT",
    "aD": "PICK UP",
    "aE": "TURN ON",
    "aF": "TURN OFF",
    "aG": "EAT",
}

friendly_names = {
    "aI": "EGGS",
    "aJ": "MILK",
    "aK": "CHEESE",
    "aL": "KEY",
    "aM": "BOWL",
    "aN": "PAN",
    "aO": "UTENSILS",

    "aP": "TO BEDROOM",
    "aV": "TO KITCHEN",
    "aR": "OVEN",
    "aS": "COUNTER",
    "aT": "FRIDGE",

    "aU": "CUPBOARD",
    "aQ": "BED",
    "aW": "STOVETOP",
    "aX": "SHELVES",
    "aY": "PLATE",
    "aZ": "PICTURE"
}

action_mappings = {
    "open": "aA",
    # "close": "aB",
    "look_at": "aC",
    "pick_up": "aD",
    "turn_on": "aE",
    "turn_off": "aF",
    "eat": "aG",
    "quit": "aH",

    "eggs": "aI",
    "milk": "aJ",
    "cheese": "aK",
    "key": "aL",
    "bowl": "aM",
    "pan": "aN",
    "whisk": "aO",

    "bedroom_move": "aP",
    "kitchen_move": "aV",
    "oven": "aR",
    "counter": "aS",
    "fridge": "aT",

    "cupboard": "aU",
    "bed": "aQ",
    "burner": "aW",
    "shelves": "aX",
    "plate": "aY",
    "picture": "aZ"
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


def change_room(room, do_text=True):
    global current_room
    global current_scans
    if current_room is not None:
        current_room.exit(do_text)
    room.enter(do_text)
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
        return True

    return change


def print_command(rec):
    def do_print():
        reg.print_receipt(rec)
        return True

    return do_print


def already_have(thing):
    reg.write_to_screen("Already have the" + friendly_names[thing])
    time.sleep(1.5)


def dont_have(thing):
    reg.clear_screen()
    reg.write_to_screen("Don't have the  " + friendly_names[thing] + "!")
    time.sleep(1.5)


def transfer_item(item_id, from_loc, to_loc):
    interacts = from_loc.interactables_with_id(item_id)
    to_loc.add_interactables(interacts)
    from_loc.remove_interactables_with_id(item_id)


def lose_inventory(name):
    reg.print_receipt(
        "misc_dropitem",
        [
            ("{ITEM}", friendly_names[name])
        ]
    )


def gain_inventory(name):
    reg.print_receipt("inventory_" + name)


hasBowl = False
hasKey = False
hasEggs = False
hasMilk = False
hasCheese = False

bowlState = 0
panState = 0
bowlOnCounter = False
bowlHasEggs = False
bowlHasMilk = False

panOnStove = False
burnerOn = False

doorUnlocked = False
cupboardUnlocked = False
bowlTaken = False
whiskTaken = False
eggsTaken = False
milkTaken = False

milkUsed = False
milkEatAttempts = 0

plateHasOmelet = False


bedroom = Room(
    "bedroom",
    [],
    [
        RoomReplacement(
            "bowl_gone1",
            (0, 0),
            "bedroom_nobowl",
            lambda: bowlTaken
        ),
        RoomReplacement(
            "bowl_gone2",
            (0, 0),
            "bedroom_spill",
            lambda: bowlTaken
        ),
        RoomReplacement(
            "key_gone",
            (0, 0),
            "bedroom_nokey",
            lambda: hasKey
        )
    ],
    print_command("ENTER_bedroom1"),
    print_command("ENTER_bedroom2")
)

kitchen = Room(
    "kitchen",
    [],
    [
        RoomReplacement(
            "kitchen_cupboardopen",
            (0, 0),
            "kitchen_cupboardopen",
            lambda: panOnStove
        ),
        RoomReplacement(
            "kitchen_panstove",
            (0, 0),
            "kitchen_panstove",
            lambda: panOnStove
        ),
        RoomReplacement(
            "kitchen_whiskgone",
            (0, 0),
            "kitchen_whiskgone",
            lambda: panState == 1
        ),
        RoomReplacement(
            "kitchen_bowlempty",
            (0, 0),
            "kitchen_bowlempty",
            lambda: bowlOnCounter and not hasBowl and not panState >= 1 and not plateHasOmelet
        ),
        RoomReplacement(
            "kitchen_bowlwhisk",
            (0, 0),
            "kitchen_bowlwhisk",
            lambda: bowlState == 2 and not hasBowl and not panState >= 1 and not plateHasOmelet
        )
    ],
    print_command("ENTER_kitchen1"),
    print_command("ENTER_kitchen2")
)

stove = Room(
    "stove",
    [],
    [
        RoomReplacement(
            "burner_panempty1",
            (0, 0),
            "stove_emptypan",
            lambda: panOnStove
        ),
        RoomReplacement(
            "burner_panempty2",
            (0, 0),
            "stove_nohangingpan",
            lambda: panOnStove
        ),
        RoomReplacement(
            "burner_panuncooked",
            (0, 0),
            "stove_uncookedpan",
            lambda: panState == 1
        ),
        RoomReplacement(
            "burner_pancooked",
            (0, 0),
            "stove_cookedpan",
            lambda: panState == 2
        ),
        RoomReplacement(
            "burner_panomelet",
            (0, 0),
            "stove_omeletpan",
            lambda: panState == 3
        )
    ],
    print_command("ENTER_stove1")
)

counter = Room(
    "counter",
    [],
    [
        RoomReplacement(
            "counter_bowlempty",
            (0, 0),
            "counter_bowlempty",
            lambda: bowlOnCounter
        ),
        RoomReplacement(
            "counter_bowleggs",
            (0, 0),
            "counter_bowleggs",
            lambda: bowlHasEggs
        ),
        RoomReplacement(
            "counter_bowlwhisk",
            (0, 0),
            "counter_bowlwhisk",
            lambda: bowlState == 2
        ),
        RoomReplacement(
            "counter_nowhisk",
            (0, 0),
            "counter_nowhisk",
            lambda: bowlState == 2
        )
    ],
    print_command("ENTER_counter1")
)

fridge = Room(
    "fridge",
    [],
    [
        RoomReplacement(
            "fridge_noeggs",
            (0, 0),
            "fridge_noeggs",
            lambda: eggsTaken
        ),
        RoomReplacement(
            "fridge_nomilk",
            (0, 0),
            "fridge_nomilk",
            lambda: milkTaken
        )
    ],
    print_command("ENTER_fridge1")
)

inventory = Inventory(
    []
)


# INTERACTION SETS ######################################
def bowl_interactions():
    def look():
        if bowlState == 0:
            # flower
            reg.print_receipt("bowl_lookflower")
        elif bowlState == 1:
            # picked up
            things_in_it = "The bowl is empty."
            if bowlHasMilk and bowlHasEggs:
                things_in_it = "The bowl has two eggs and a splash of milk. But they aren't mixed..."
            elif bowlHasMilk:
                things_in_it = "The bowl has milk."
            elif bowlHasEggs:
                things_in_it = "The bowl has two eggs."
            reg.print_receipt(
                "bowl_lookincomplete",
                [
                    ("{BOWL_STATE}", things_in_it)
                ]
            )
        elif bowlState == 2:
            # whisked
            reg.print_receipt("bowl_lookwhisked")

        return True

    def pick_up():
        global hasBowl
        global bowlTaken
        global bowlState
        if hasBowl:
            already_have(am("bowl"))
        elif bowlOnCounter and bowlState != 2:
            reg.print_receipt("bowl_nopickup")
        else:
            if bowlTaken:
                reg.print_receipt("bowl_pickupwhisked")
                gain_inventory("bowlwhisked")
                transfer_item(am("bowl"), counter, inventory)
                kitchen.replacement_with_id("kitchen_bowlempty").re_enable()
                kitchen.replacement_with_id("kitchen_bowlwhisk").re_enable()

                counter.replacement_with_id("counter_bowlempty").re_enable()
                counter.replacement_with_id("counter_bowleggs").re_enable()
                counter.replacement_with_id("counter_bowlwhisk").re_enable()
            else:
                reg.print_receipt("bowl_pickupflower")
                gain_inventory("bowl")
                transfer_item(am("bowl"), bedroom, inventory)
                bowlTaken = True
                bowlState = 1
                bedroom.draw_room()
            hasBowl = True

        return True

    def eggs():
        global bowlHasEggs
        global hasEggs
        if not hasEggs:
            dont_have(am("eggs"))
            return True
        if not bowlOnCounter:
            reg.print_receipt("bowl_notoncounter")
            return True
        bowlHasEggs = True
        reg.print_receipt("bowl_eggs")
        hasEggs = False
        lose_inventory(am("eggs"))
        return True

    def milk():
        global bowlHasMilk
        global milkUsed
        if not hasMilk:
            dont_have(am("milk"))
            return True
        if not bowlOnCounter:
            if not bowlTaken:
                reg.print_receipt("bowl_milkflower")
                return True
            reg.print_receipt("bowl_notoncounter")
            return True
        if bowlHasMilk:
            reg.print_receipt("bowl_milkalready")
            return True
        bowlHasMilk = True
        reg.print_receipt("bowl_milk")
        milkUsed = True
        return True

    def whisk():
        global bowlState
        if bowlOnCounter and bowlHasMilk and bowlHasEggs and bowlState == 1:
            reg.print_receipt("bowl_whisk")
            bowlState = 2
            counter.draw_room()
        else:
            reg.print_receipt("bowl_nowhisk")
        return True

    return [
        Interactable(
            am("bowl"),
            [am("look_at")],
            look
        ),
        Interactable(
            am("bowl"),
            [am("eat")],
            print_command("bowl_eat")
        ),
        Interactable(
            am("bowl"),
            [am("pick_up")],
            pick_up
        ),
        Interactable(
            am("bowl"),
            [am("eggs")],
            eggs
        ),
        Interactable(
            am("bowl"),
            [am("milk")],
            milk
        ),
        Interactable(
            am("bowl"),
            [am("whisk")],
            whisk
        ),
        Interactable(
            am("bowl"),
            [am("cheese")],
            print_command("misc_nocheese")
        )
    ]


def key_interactions():
    def pick_up():
        already_have(am("key"))
        return True

    return [
        Interactable(
            am("key"),
            [am("look_at")],
            print_command("key_look")
        ),
        Interactable(
            am("key"),
            [am("eat")],
            print_command("key_eat")
        ),
        Interactable(
            am("key"),
            [am("pick_up")],
            pick_up
        )
    ]


def cheese_interactions():
    def pick_up():
        already_have(am("cheese"))
        return True

    return [
        Interactable(
            am("cheese"),
            [am("look_at")],
            print_command("cheese_look")
        ),
        Interactable(
            am("cheese"),
            [am("eat")],
            print_command("cheese_eat")
        ),
        Interactable(
            am("cheese"),
            [am("pick_up")],
            pick_up
        )
    ]


def plate_interactions():
    def pick_up():
        already_have(am("plate"))
        return True

    def look():
        if plateHasOmelet:
            reg.print_receipt("plate_lookomelet")
        else:
            reg.print_receipt("plate_look")
        return True

    def eat():
        global won
        if plateHasOmelet:
            won = True
        else:
            reg.print_receipt("plate_eat")
        return True

    return [
        Interactable(
            am("plate"),
            [am("look_at")],
            look
        ),
        Interactable(
            am("plate"),
            [am("eat")],
            eat
        ),
        Interactable(
            am("plate"),
            [am("pick_up")],
            pick_up
        )
    ]


def milk_interactions():
    def pick_up():
        global hasMilk
        global milkTaken
        if hasMilk:
            already_have(am("milk"))
        elif milkTaken:
            return False
        else:
            reg.print_receipt("milk_pickup")
            gain_inventory("milk")
            transfer_item(am("milk"), fridge, inventory)
            hasMilk = True
            milkTaken = True
        return True

    def eat():
        global milkEatAttempts
        if milkTaken and not hasMilk:
            return False

        if not milkUsed:
            reg.print_receipt("milk_noeat")
            return True

        if milkEatAttempts == 4:
            reg.print_receipt("milk_eat")
            inventory.remove_interactables_with_id(am("milk"))
            lose_inventory(am("milk"))
            return True
        if milkEatAttempts == 3:
            reg.print_receipt("milk_tryeat3")
        if milkEatAttempts == 2:
            reg.print_receipt("milk_tryeat2")
        elif milkEatAttempts == 1:
            reg.print_receipt("milk_tryeat1")
        elif milkEatAttempts == 0:
            reg.print_receipt("milk_tryeat")

        milkEatAttempts += 1
        return True

    return [
        Interactable(
            am("milk"),
            [am("look_at")],
            print_command("milk_look")
        ),
        Interactable(
            am("milk"),
            [am("eat")],
            eat
        ),
        Interactable(
            am("milk"),
            [am("pick_up")],
            pick_up
        )
    ]


def eggs_interactions():
    def pick_up():
        global hasEggs
        global eggsTaken
        if hasEggs:
            already_have(am("eggs"))
        elif eggsTaken:
            return False
        else:
            reg.print_receipt("eggs_pickup")
            gain_inventory("eggs")
            transfer_item(am("eggs"), fridge, inventory)
            hasEggs = True
            eggsTaken = True
        return True

    return [
        Interactable(
            am("eggs"),
            [am("look_at")],
            print_command("eggs_look")
        ),
        Interactable(
            am("eggs"),
            [am("eat")],
            print_command("eggs_noeat")
        ),
        Interactable(
            am("eggs"),
            [am("pick_up")],
            pick_up
        )
    ]


def pan_interactions():
    def pick_up():
        if panOnStove:
            if panState == 3:
                reg.print_receipt("pan_platepickuphint")
                return True

            if burnerOn:
                reg.print_receipt("pan_nopickuptoohot")
            else:
                reg.print_receipt("pan_nopickup")

            return True

        _move_to_burner()
        return True

    def look():
        if panState == 0:
            # empty
            reg.print_receipt("pan_empty")
        elif panState == 1:
            # uncooked eggs
            reg.print_receipt("pan_uncooked")
        elif panState == 2:
            # cooked eggs
            reg.print_receipt("pan_cooked")
        elif panState == 3:
            # omelet
            reg.print_receipt("pan_omelet")
        return True

    def eat():
        if panState == 0:
            # empty
            reg.print_receipt("pan_eat")
        elif panState == 1:
            # uncooked eggs
            reg.print_receipt("pan_eateggs")
        elif panState == 2:
            # cooked eggs
            reg.print_receipt("pan_needscheese")
        elif panState == 3:
            # omelet
            reg.print_receipt("pan_eatomelet")
        return True

    def bowl():
        global panState
        if not hasBowl:
            dont_have(am("bowl"))
            return True
        if bowlState <= 1:
            return False

        if plateHasOmelet:
            reg.print_receipt("pan_nobowlomeletalready")
            return True

        if panState == 0 and bowlState == 2:
            reg.print_receipt("pan_bowl")
            panState = 1
            if burnerOn:
                panState = 2
                reg.print_receipt("pan_eggscook")
            stove.draw_room()
        elif panState >= 1:
            reg.print_receipt("pan_nobowleggsalready")
        return True

    def cheese():
        global panState
        global hasCheese
        if not hasCheese:
            dont_have(am("cheese"))
            return True
        if panState <= 1:
            reg.print_receipt("misc_nocheese")
            return True

        if panState == 2:
            reg.print_receipt("pan_cheese")
            lose_inventory(am("cheese"))
            hasCheese = False
            panState = 3
            stove.draw_room()
        return True

    def plate():
        global plateHasOmelet
        global panState

        if plateHasOmelet:
            return False

        if panState == 3:
            stove.replacement_with_id("burner_panuncooked").re_enable()
            stove.replacement_with_id("burner_pancooked").re_enable()
            stove.replacement_with_id("burner_panomelet").re_enable()
            panState = 0
            plateHasOmelet = True
            stove.draw_room()
            reg.print_receipt("pan_plate")
            gain_inventory("omelet")
            return True
        elif panState == 2:
            reg.print_receipt("pan_needscheese")

        return False

    def _move_to_burner():
        global panOnStove
        panOnStove = True
        reg.print_receipt("pan_movetoburner")
        stove.draw_room()

    return [
        Interactable(
            am("pan"),
            [am("look_at")],
            look
        ),
        Interactable(
            am("pan"),
            [am("eat")],
            eat
        ),
        Interactable(
            am("pan"),
            [am("pick_up"), am("burner")],
            pick_up
        ),
        Interactable(
            am("pan"),
            [am("bowl")],
            bowl
        ),
        Interactable(
            am("pan"),
            [am("cheese")],
            cheese
        ),
        Interactable(
            am("pan"),
            [am("plate")],
            plate
        ),
        Interactable(
            am("pan"),
            [am("eggs")],
            print_command("pan_noeggs")
        )
    ]


def tobedroom_interactions():
    return [
        Interactable(
            am("bedroom_move"),
            ["ANY", None],
            change_room_command(bedroom)
        )
    ]


def tokitchen_interactions():
    def try_door():
        if doorUnlocked:
            print("unlocked! moving")
            change_room(kitchen)
        else:
            reg.print_receipt("door_locked")
        return True

    def key():
        global doorUnlocked
        if not hasKey:
            dont_have(am("key"))
            return True

        if doorUnlocked:
            reg.print_receipt("door_nokey")
        else:
            reg.print_receipt("door_key")
            doorUnlocked = True
        return True

    def look_at():
        if current_room == bedroom:
            reg.print_receipt("door_look")
            return True
        return False

    def try_any():
        if doorUnlocked:
            change_room(kitchen)
            return True
        return False

    return [
        Interactable(
            am("kitchen_move"),
            [am("open")],
            try_door
        ),
        Interactable(
            am("kitchen_move"),
            [am("look_at")],
            look_at
        ),
        Interactable(
            am("kitchen_move"),
            [am("key")],
            key
        ),
        Interactable(
            am("kitchen_move"),
            ["ANY", None],
            try_any
        )
    ]


def oven_interactions():
    def turn_on():
        global burnerOn
        global panState
        if burnerOn:
            reg.print_receipt("burner_noturnon")
        else:
            burnerOn = True
            reg.print_receipt("burner_turnon")
            if panState == 1:
                panState = 2
                reg.print_receipt("pan_eggscook")
                change_room(stove, False)
        return True

    def turn_off():
        global burnerOn
        if not burnerOn:
            reg.print_receipt("burner_noturnoff")
        elif panState == 2:
            reg.print_receipt("burner_noturnoffcooked")
        else:
            burnerOn = False
            reg.print_receipt("burner_turnoff")
        return True

    def bowl():
        global panState
        if not hasBowl:
            dont_have(am("bowl"))
            return True
        if bowlState <= 1:
            return False

        if panState == 0 and bowlState == 2:
            reg.print_receipt("pan_bowl")
            panState = 1
            change_room(stove, False)
            stove.draw_room()
        elif panState >= 1:
            reg.print_receipt("pan_nobowl")
        return True

    def cheese():
        global panState
        global hasCheese
        if not hasCheese:
            dont_have(am("cheese"))
            return True
        if panState <= 1:
            reg.print_receipt("misc_nocheese")
            return True

        if panState == 2:
            reg.print_receipt("pan_cheese")
            lose_inventory(am("cheese"))
            hasCheese = False
            panState = 3
            change_room(stove, False)
            stove.draw_room()
        return True

    def plate():
        global plateHasOmelet
        global panState

        if plateHasOmelet:
            return False

        if panState == 3:
            stove.replacement_with_id("burner_panuncooked").re_enable()
            stove.replacement_with_id("burner_pancooked").re_enable()
            stove.replacement_with_id("burner_panomelet").re_enable()
            panState = 0
            plateHasOmelet = True
            reg.print_receipt("pan_plate")
            gain_inventory("omelet")
            return True

        return False

    return [
        Interactable(
            am("oven"),
            [am("look_at")],
            change_room_command(stove)
        ),
        Interactable(
            am("oven"),
            [am("open")],
            print_command("oven_noopen")
        ),
        Interactable(
            am("oven"),
            [am("turn_on")],
            turn_on
        ),
        Interactable(
            am("oven"),
            [am("turn_off")],
            turn_off
        ),
        Interactable(
            am("oven"),
            [am("cheese")],
            cheese
        ),
        Interactable(
            am("oven"),
            [am("plate")],
            plate
        ),
        Interactable(
            am("oven"),
            [am("bowl")],
            bowl
        )
    ]


def counter_interactions():
    def try_change_room():
        if current_room == counter:
            reg.print_receipt("counter_look")
        else:
            change_room(counter)
        return True

    def bowl():
        global bowlOnCounter
        global hasBowl
        if not hasBowl:
            dont_have(am("bowl"))
            return True
        if bowlOnCounter:
            return False

        if bowlState == 2:
            reg.print_receipt("counter_nobowl")
        elif bowlState == 1:
            reg.print_receipt("counter_bowl")
            lose_inventory(am("bowl"))
            transfer_item(am("bowl"), inventory, counter)
            hasBowl = False
            bowlOnCounter = True
            if current_room == kitchen:
                change_room(counter, False)
            else:
                counter.draw_room()

        return True

    return [
        Interactable(
            am("counter"),
            [am("look_at")],
            try_change_room
        ),
        Interactable(
            am("counter"),
            [am("bowl")],
            bowl
        )
    ]


def fridge_interactions():
    def eggs():
        global hasEggs
        global eggsTaken
        if not hasEggs:
            dont_have(am("eggs"))
            return True
        hasEggs = False
        eggsTaken = False
        reg.print_receipt("fridge_puteggs")
        lose_inventory(am("eggs"))
        transfer_item(am("eggs"), inventory, fridge)

        fridge.replacement_with_id("fridge_noeggs").re_enable()
        return True

    def milk():
        global hasMilk
        global milkTaken
        if not hasMilk:
            dont_have(am("milk"))
            return True
        hasMilk = False
        milkTaken = False
        reg.print_receipt("fridge_putmilk")
        lose_inventory(am("milk"))
        transfer_item(am("milk"), inventory, fridge)

        fridge.replacement_with_id("fridge_nomilk").re_enable()
        return True

    return [
        Interactable(
            am("fridge"),
            [am("open")],
            change_room_command(fridge)
        ),
        Interactable(
            am("fridge"),
            [am("turn_off")],
            print_command("fridge_noturnoff")
        ),
        Interactable(
            am("fridge"),
            [am("look_at")],
            print_command("fridge_look")
        ),
        Interactable(
            am("fridge"),
            [am("eggs")],
            eggs
        ),
        Interactable(
            am("fridge"),
            [am("milk")],
            milk
        ),
        Interactable(
            am("fridge"),
            [am("cheese")],
            print_command("misc_nocheese")
        )
    ]


def burner_interactions():
    def turn_on():
        global burnerOn
        global panState
        if burnerOn:
            reg.print_receipt("burner_noturnon")
        else:
            burnerOn = True
            reg.print_receipt("burner_turnon")
            if panState == 1:
                panState = 2
                reg.print_receipt("pan_eggscook")
        return True

    def turn_off():
        global burnerOn
        if not burnerOn:
            reg.print_receipt("burner_noturnoff")
        elif panState == 2:
            reg.print_receipt("burner_noturnoffcooked")
        else:
            burnerOn = False
            reg.print_receipt("burner_turnoff")
        return True

    def look_at():
        reg.print_receipt(
            "burner_look",
            [
                ("{BURNER_STATUS}", "on" if burnerOn else "off")
            ]
        )
        return True

    return [
        Interactable(
            am("burner"),
            [am("turn_on")],
            turn_on
        ),
        Interactable(
            am("burner"),
            [am("turn_off")],
            turn_off
        ),
        Interactable(
            am("burner"),
            [am("look_at")],
            look_at
        ),
    ]


def whisk_interactions():
    return [
        Interactable(
            am("whisk"),
            [am("look_at")],
            print_command("whisk_look")
        ),
        Interactable(
            am("whisk"),
            [am("eat")],
            print_command("whisk_eat")
        ),
        Interactable(
            am("whisk"),
            [am("pick_up")],
            print_command("whisk_nopickup")
        )
    ]


def cupboard_interactions():
    def try_open():
        global cupboardUnlocked
        global hasCheese
        if cupboardUnlocked:
            return False

        reg.print_receipt("cupboard_needscode")
        code = reg.query_keypad("4 DIGITS")
        if code == "1548":
            reg.print_receipt("cupboard_correct")
            cupboardUnlocked = True
            hasCheese = True
            gain_inventory("cheese")
            inventory.add_interactables(cheese_interactions())
        else:
            reg.print_receipt("cupboard_incorrect")
        return True

    def look_at():
        if cupboardUnlocked:
            reg.print_receipt("cupboard_lookopen")
        else:
            reg.print_receipt("cupboard_look")
        return True

    return [
        Interactable(
            am("cupboard"),
            [am("look_at")],
            look_at
        ),
        Interactable(
            am("cupboard"),
            [am("open")],
            try_open
        ),
        Interactable(
            am("cupboard"),
            [am("cheese")],
            print_command("cupboard_nocheese")
        ),
        Interactable(
            am("cupboard"),
            [am("key")],
            print_command("cupboard_nokey")
        )
    ]


def shelves_interactions():
    def eggs():
        global hasEggs
        global eggsTaken
        if not hasEggs:
            dont_have(am("eggs"))
            return True
        hasEggs = False
        eggsTaken = False
        reg.print_receipt("fridge_puteggs")
        lose_inventory(am("eggs"))
        transfer_item(am("eggs"), inventory, fridge)
        return True

    def milk():
        global hasMilk
        global milkTaken
        if not hasMilk:
            dont_have(am("milk"))
            return True
        hasMilk = False
        milkTaken = False
        reg.print_receipt("fridge_putmilk")
        lose_inventory(am("milk"))
        transfer_item(am("milk"), inventory, fridge)
        return True

    return [
        Interactable(
            am("shelves"),
            [am("look_at"), am("pick_up")],
            print_command("shelves_look")
        ),
        Interactable(
            am("shelves"),
            [am("eggs")],
            eggs
        ),
        Interactable(
            am("shelves"),
            [am("milk")],
            milk
        ),
        Interactable(
            am("shelves"),
            [am("cheese")],
            print_command("misc_nocheese")
        )
    ]


def picture_interactions():
    return [
        Interactable(
            am("picture"),
            [am("look_at")],
            print_command("picture_look")
        ),
        Interactable(
            am("picture"),
            [am("eat")],
            print_command("picture_eat")
        ),
        Interactable(
            am("picture"),
            [am("pick_up")],
            print_command("picture_pickup")
        )
    ]


def bed_interactions():
    def look_at():
        global hasKey
        if not hasKey:
            reg.print_receipt("bed_lookkey")
            hasKey = True
            gain_inventory("key")
            inventory.add_interactables(key_interactions())
        else:
            reg.print_receipt("bed_look")
        return True

    def pick_up():
        global hasKey
        if not hasKey:
            reg.print_receipt("bed_pickupkey")
            hasKey = True
            gain_inventory("key")
            inventory.add_interactables(key_interactions())
        else:
            reg.print_receipt("bed_pickup")
        return True

    return [
        Interactable(
            am("bed"),
            [am("look_at")],
            look_at
        ),
        Interactable(
            am("bed"),
            [am("pick_up")],
            pick_up
        )
    ]

##################################################


inventory.add_interactables(plate_interactions())

bedroom.add_interactables(bed_interactions())
bedroom.add_interactables(bowl_interactions())
bedroom.add_interactables(tokitchen_interactions())

kitchen.add_interactables(oven_interactions())
kitchen.add_interactables(fridge_interactions())
kitchen.add_interactables(counter_interactions())
kitchen.add_interactables(tobedroom_interactions())
kitchen.add_interactables(cupboard_interactions())

counter.add_interactables(whisk_interactions())
counter.add_interactables(counter_interactions())
counter.add_interactables(tokitchen_interactions())

stove.add_interactables(burner_interactions())
stove.add_interactables(pan_interactions())
stove.add_interactables(picture_interactions())
stove.add_interactables(tokitchen_interactions())

fridge.add_interactables(shelves_interactions())
fridge.add_interactables(eggs_interactions())
fridge.add_interactables(milk_interactions())
fridge.add_interactables(tokitchen_interactions())


change_room(bedroom)


def add_scan(bc, __):
    global current_scans
    current_scans.append(bc)


for bc_id in action_mappings.values():
    reg.add_valid_barcode(bc_id, add_scan)

reg.clear_screen()
reg.write_to_screen(make_action_text())
while not done and not won:
    reg.query_scanner(filter_digits=True)
    if am("quit") in current_scans:
        done = True
        reg.pop_drawer()
    else:
        reg.clear_screen()
        reg.write_to_screen(make_action_text())

        result = current_room.poll_interactions(current_scans)
        if not result:
            result = inventory.poll_interactions(current_scans)
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

if won:
    reg.print_receipt("WIN")
    pass

time.sleep(3)
