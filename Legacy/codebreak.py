from registration import Registration

reg = Registration()


reg.print_receipt("CB1")
reg.pop_drawer()
code = reg.query_keypad("4 DIGIT CODE:", 4, True)
reg.print_receipt("CB2")


def get_hint(attempt):
    code_split = [*code]
    attempt_split = [*attempt]
    ps = 0
    ns = 0
    for i in range(0, 4):
        if code_split[i] == attempt_split[i]:
            ps += 1
            code_split[i] = None
            attempt_split[i] = None
    for i in range(0, 4):
        if attempt_split[i] is not None and attempt_split[i] in code_split:
            ns += 1
            code_split[code_split.index(attempt_split[i])] = None
    return "".join(["P"]*ps + ["N"]*ns)


guess = ""
guess_number = 0
while guess != code:
    guess_number += 1
    guess = reg.query_keypad("GUESS #" + str(guess_number) + ":", 4, True)

    if guess == code:
        reg.pop_drawer()
        reg.print_receipt("CBwin", [
            ("{COMBINATION}", code),
            ("{TRIES}", str(guess_number))
        ])
    else:
        reg.print_receipt("CBguess", [
            ("{GUESS}", guess),
            ("{HINT}", get_hint(guess))
        ])
