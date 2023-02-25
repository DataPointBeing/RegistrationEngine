import time

from registration import Registration

reg = Registration(0, 0)


def ice_cream_response(flavor, __):
    reg.remove_valid_barcode("Y")
    reg.remove_valid_barcode("K")
    reg.remove_valid_barcode("D")
    reg.remove_valid_barcode("Z")
    repl = None
    if flavor == "D":
        repl = [
            ("TAG1", "but cash"),
            ("TAG2", "registers"),
            ("TAG3", "can't eat"),
            ("TAG4", "ice cream.")
        ]
    elif flavor == "Y":
        repl = [
            ("TAG1", "I think"),
            ("TAG2", "mint is"),
            ("TAG3", "terrible"),
            ("TAG4", "though.")
        ]
    elif flavor == "K":
        repl = [
            ("TAG1", "and the"),
            ("TAG2", "objectively"),
            ("TAG3", "correct"),
            ("TAG4", "answer.")
        ]
    elif flavor == "Z":
        reg.print_receipt("CONVO6")
        return

    reg.print_receipt("CONVO5", repl)
    reg.add_valid_barcode("B", bye)
    reg.add_valid_barcode("H", bye)
    reg.query_scanner("Scan a response:")


def introduction(intro, __):
    reg.remove_valid_barcode("A")
    reg.remove_valid_barcode("W")
    if intro == "W":
        reg.print_receipt("CONVO2")
        reg.add_valid_barcode("Q", couldnt_you_tell)
        reg.add_valid_barcode("J", couldnt_you_tell)
        reg.query_scanner("Scan a response:")
    else:
        reg.print_receipt("CONVO4")
        reg.add_valid_barcode("Y", ice_cream_response)
        reg.add_valid_barcode("K", ice_cream_response)
        reg.add_valid_barcode("D", ice_cream_response)
        reg.add_valid_barcode("Z", ice_cream_response)
        reg.query_scanner("Scan a response:")


def couldnt_you_tell(_, __):
    reg.remove_valid_barcode("Q")
    reg.remove_valid_barcode("J")
    reg.print_receipt("CONVO3")
    reg.print_receipt("CONVO4")
    reg.add_valid_barcode("Y", ice_cream_response)
    reg.add_valid_barcode("K", ice_cream_response)
    reg.add_valid_barcode("D", ice_cream_response)
    reg.add_valid_barcode("Z", ice_cream_response)
    reg.query_scanner("Scan a response:")


def bye(response, __):
    reg.remove_valid_barcode("B")
    reg.remove_valid_barcode("H")
    if response == "B":
        reg.print_receipt("CONVO7")
        return
    reg.print_receipt("CONVO8")
    reg.add_valid_barcode("T", lingering)
    reg.query_scanner("Scan a response:")


def lingering(_, __):
    reg.remove_valid_barcode("T")
    reg.print_receipt("CONVO9")







reg.print_receipt("CONVO1")
reg.add_valid_barcode("A", introduction)
reg.add_valid_barcode("W", introduction)
reg.query_scanner("Scan a response:")