# filesystem
import configparser
from os import path
from pathlib import Path
import sys

# Nativas
import json
from typing import Any

class Metadata:
    info:Any = None

    @staticmethod
    def getInfo() -> Any: 
        if Metadata.info is None:  # Read only once, lazy.
            print("inicialización de metadatos custom")
            Metadata.info = configparser.ConfigParser()
            main_path = path.realpath(sys.argv[0]) if sys.argv[0] else ''
            parent_path = Path(main_path).parent
            resources_path = path.join(parent_path, "resources/")
            conf_path = path.join(resources_path, 'metadata.cfg')
            print('ruta de fichero: '+conf_path)
            if path.exists(conf_path):
                Metadata.info.read(conf_path)
                {section: print("Sección {0}: {1}".format(section, json.dumps(dict(Metadata.info[section])))) for section in Metadata.info.sections()}
            else:
                print('ruta no existe')
                return None
        return Metadata.info


if __name__ == '__main__':
    print("prueba de metadata:")
    print(Metadata.getInfo())
