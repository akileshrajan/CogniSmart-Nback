from PIL import Image
import os, sys

path = "/home/akilesh/PycharmProjects/CogniSmart-Nback/AppData/Nback_visual/"
dirs = os.listdir(path)

for item in dirs:
    if os.path.isfile(path+item):
        im = Image.open(path+item)
        f,e = os.path.splitext(path+item)
        imResize = im.resize((195,160),Image.ANTIALIAS)
        imResize.save(f+e,quality=90)
