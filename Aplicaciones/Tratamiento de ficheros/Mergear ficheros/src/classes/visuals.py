#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dependencias de terceros
from tkinter import Tk,Frame,Label,Button,Entry,W
from tkinter import ttk
from tkinter import filedialog
from filecmp import dircmp

import configparser
import logging
# Dependencias propias
import sys

from arq_decorators import arq_decorator


@arq_decorator((),conf_filename='resources\\environment.cfg')
class Panel(Tk):
    # Declaración de tipos para mejorar legibilidad (OPCIONAL)
    logger = logging.getLogger().__class__
    confMap = configparser.ConfigParser().__class__

    def __init__(self):
        super(Panel, self).__init__()
        self.title("Mergeo de ficheros")
        self.row_col = {
            "row_count" : 0,
            "rows_last_pos" : []
        }
        
        Label(self, 
         text="First Name").grid(row=0)
        Label(self, text="Last Name").grid(row=1)

        e1 = Entry(self)
        e2 = Entry(self)

        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)

        Button(self, 
                text='Quit', 
                command=self.quit).grid(row=3, 
                                            column=0, 
                                            sticky=W, 
                                            pady=4)

    """
    ******
    SCENES
    ******
    """
    def scene_mergeFiles(self):
        # Variables fichero 1
        button_text_1="Seleccionar primer fichero"
        label_text_1="Seleccionar primer fichero"
        row_1 = self.__new_row()
        col_1 = self.__new_col(row_1)
        # Variables fichero 2
        text_file_2 ="Seleccionar segundo fichero"
        row_2 = self.__new_row()
        col_2 = self.__new_col(row_2)
        # visuals fichero 1
        self.__label(label_text_1,row_1,col_1)
        self.__button(button_text_1,self.__command_resourceDialog,row_1,col_1)
        self.__button(text_file_2,self.__command_resourceDialog,row_2,col_2)

    """
    *******
    VISUALS
    *******
    """
    def __button(self, c_text, c_command, c_row, c_column, *args, **kwargs):
        """
        Añade un botón al panel
        """
        button = ttk.Button(self.labelFrame, text = "Seleccionar fichero",command = c_command(*args, **kwargs))
        button.grid(column = c_column, row = c_row)
    
    def __label(self,c_text, c_row, c_column):
        """
        Añade una etiqueta al panel
        """
        Label(self,text=c_text).grid(column = c_column, row = c_row)
 
    """
    ********
    COMMANDS
    ********
    """
    def __command_resourceDialog(self, *args, **kwargs):
        Label(self,text="First Name").grid(row=self.row_col["row_count"])
        filename = filedialog.askopenfilename(initialdir =  "/", title = "Selecciona un fichero", filetype =
        (("ficheros de propiedades","*.properties"),("todos los ficheros","*.*")) )

        self.logger.info("Fichero seleccionado: %s",filename)
        self.label = ttk.Label(self.labelFrame, text = "")
        self.label.grid(column = 1, row = 2)
        self.label.configure(text = filename)

        

    def merge_files(self):
        self.logger.info("logger utilizado en clase panel correctamente")
    

    """
    ***********
    CLASS TOOLS
    ***********
    """
    def __new_row(self):
        row_aux = self.row_col["row_count"]
        self.row_col["row_count"] = self.row_col["row_count"] + 1
        self.row_col["rows_last_pos"][row_aux] = 0
        return row_aux
    
    def __new_col(self,row):
        col_aux = self.row_col["rows_last_pos"][row] = 0
        self.row_col["rows_last_pos"][row] = self.row_col["rows_last_pos"][row] + 1
        return col_aux
    """
    *************
    TEST de clase
    *************
    """
    def test_properties(self):
        if not bool(self.confMap):
            self.logger.error("MAPA DE CONFIGURACIÓN NO DEFINIDO. Se cancela el arranque")
            return False
        self.logger.info("PROPIEDADES cargadas: %s",self.confMap)
        #section: {test_properties = test_properties + "Seccion:"+section,dict(self.confMap[section])} for section in self.confMap.sections()
        self.logger.info("TEST PROPIEDADES: ¡cargadas correctamente!")
        return True
        
    