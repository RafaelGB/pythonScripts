# Basic
import configparser
import logging
# Filesystem
from os import path
from pathlib import Path
import sys

class ConfigService:

    def __init__(self):
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))

        conf_path = path.join(self.parent_path, "resources\\arq_conf.cfg")
        print("Ruta de configuración general: ",conf_path)
        self.confMap = configparser.ConfigParser()
        self.confMap.read(conf_path)
        {section: print("Seccion:"+section,dict(self.confMap[section])) for section in self.confMap.sections()}
    
    def getProperty(self, group, key):
        if group in self.confMap:
            if key in self.confMap[group]:
                return self.confMap[group][key]
            else:
                return None
        else:
            return None
    
    def getPropertyDefault(self, group, key, defaultValue):
        propertyValue = self.getProperty(group,key)
        return (propertyValue, defaultValue)[propertyValue == None]