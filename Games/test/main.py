import random
import time

from registration import Registration

reg = Registration.engine()

reg.pop_drawer()

reg.print_image("Assets/Images/crab.png")

time.sleep(3)
