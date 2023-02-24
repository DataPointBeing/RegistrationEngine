import random
import time

from registration import Registration

reg = Registration(0, 0)

result = reg.query_keypad("haha wow what")
print("I got: " + result)
