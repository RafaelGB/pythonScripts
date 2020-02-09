#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dependencias propias
from decorators.panel_decorator import architecture_Decorator
from tkinter import Tk
from tkinter import ttk
from tkinter import filedialog
import logging

@architecture_Decorator((),conf_filename='mergeConfiguration.conf')
class Panel(Tk):
    # Declaración de tipos para mejorar legibilidad (OPCIONAL)
    logger = logging.getLogger().__class__
    confMap = {}

    def __init__(self):
        super(Panel, self).__init__()
        self.title("Python Tkinter Dialog Widget")
        self.minsize(640, 400)

 
        self.labelFrame = ttk.LabelFrame(self, text = "Open File")
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 20)
        self.button()    

    def button(self):
        button = ttk.Button(self.labelFrame, text = "Browse A File",command = self.fileDialog)
        button.grid(column = 1, row = 1)
 
 
    def fileDialog(self):
 
        self.filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
        (("jpeg files","*.jpg"),("all files","*.*")) )
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = self.filename)

    def merge_files(self):
        self.logger.info("logger utilizado en clase panel correctamente")
    
    """
    *************
    TEST de clase
    *************
    """
    def test_properties(self):
        if not bool(self.confMap):
            self.logger.error("MAPA DE CONFIGURACIÓN NO DEFINIDO. Se cancela el arranque")
            return False
        self.logger.debug("PROPIEDADES cargadas: %s",self.confMap)
        self.logger.info("TEST PROPIEDADES: ¡cargadas correctamente!")
        return True
        
    