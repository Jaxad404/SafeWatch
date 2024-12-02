import hashlib
import pandas as pd
import csv
from PIL import Image

csvInfo = []
imgFile = ''

def ReSize(imgFile):
    img = Image.open(imgFile)
    img = img.resize((248, 248))
    img.save(imgFile)
    print("[+] Resizing Successfull")

def hashedPwd(pwd):
    sha512 = hashlib.sha512()
    pwd = bytes(pwd, "utf-8")
    sha512.update(pwd)
    return sha512.hexdigest()


def load_csv(csvInfo):
    filename = '../model/MCI_2014_to_2019.csv'
    with open(filename, newline='\n') as file:
        reader = csv.reader(file, delimiter=',')
        for idx, val in enumerate(reader):
            if idx == 0:
                continue

            val.reverse()
            val.pop()
            val.reverse()
            csvInfo.append(tuple(val))






