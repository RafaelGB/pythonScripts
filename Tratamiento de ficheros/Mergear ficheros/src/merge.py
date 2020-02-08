
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Librerias nativas
import sys
import traceback

# Librerias de terceros
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import shutil

# Dependencias propias
from decorators.panel_decorator import PanelDecorator
from classes.visuals import Panel
def start(*args, **kwargs):
    panel = Panel()
    panel.merge_files()
    return None

if __name__ == '__main__':
  start()
"""

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
print(filename)
print("Mergeando en el fichero ",filename3)
with open(filename3, "wb") as wfd:
    for f in [filename1, filename2]:
        with open(f, "rb") as fd:
            shutil.copyfileobj(fd, wfd, 1024*1024*10)
print("\nContenido mergeado correctamente.!")
print("(Quieres verlo? (y/n): ")
check = input()
if check == 'n':
    exit()
else:
    print()
    c = open(filename3, "r")
    print(c.read())
    c.close()
"""