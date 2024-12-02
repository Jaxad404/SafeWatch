import os

def get_fonts():
    font_types = []
    with open('fonts.txt', 'r') as file:
        for line in file.readlines():
            lin = line.split(' ')
            lin = str(lin[8:10]).split('(')[-1]
            if lin.startswith('fname='):
                font_name = lin.split(' ')[0].split('fname=')[1].split(',')[0].split('/')[-1].split('.')[0]
                font_file = lin.split(' ')
                font_file = lin.split(',')[0].split('fname=')[1]
                font_types.append(font_file)
    return list(set(font_types))

print(len(get_fonts()))