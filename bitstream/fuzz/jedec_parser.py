import re

def get_bitmap(str):
    for line in re.finditer("L\d+ ([01]+) ([01]+)", str):
        print(line)