import os
import time

from registration import Registration

def main():
    unlocked_yet = 0

    reg = Registration.engine()

    def unlock_message():
        nonlocal unlocked_yet
        if unlocked_yet == 2:
            reg.print_receipt("PZtwo")
            return
        reg.print_receipt("PZone")

    def q_comboA(_, __):
        x = reg.query_keypad("Combo A Guess:", 3, True)
        if x == "405":
            reg.remove_valid_barcode("A")
            nonlocal unlocked_yet
            unlocked_yet += 1
            unlock_message()
            return

        os.system('cls')
        print('WRONG COMBO')
        time.sleep(3)

    def q_comboB(_, __):
        x = reg.query_keypad("Combo B Guess:", 3, True)
        if x == "222":
            reg.remove_valid_barcode("B")
            nonlocal unlocked_yet
            unlocked_yet += 1
            unlock_message()
            return

        os.system('cls')
        print('WRONG COMBO')
        time.sleep(3)

    def printer(_, __):
        reg.print_receipt("PZbox")

    def school_id(_, __):
        reg.print_receipt("PZid")

    def norman(_, __):
        reg.print_receipt("PZnorman")
        reg.add_valid_barcode("A", q_comboA)
        reg.add_valid_barcode("B", q_comboB)
        reg.add_valid_barcode("X000N0XR2L", printer)  # printer
        reg.add_valid_barcode("804469733", school_id)  # ID

    reg.print_receipt("PZ1")
    reg.add_valid_barcode("9780465050659", norman)  # Norman

    while unlocked_yet < 2:
        reg.query_scanner("SCAN SOMETHING")

    reg.pop_drawer()
    time.sleep(3)


main()
