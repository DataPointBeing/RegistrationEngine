import PIL
from PIL import Image

im1 = Image.open("Assets/Images/counter.png")
im2 = Image.open("Assets/Images/counter_bowlwhisk.png")

im1.paste(im2, mask=im2)

im1.show()
