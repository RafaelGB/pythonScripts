import configparser
import json
from os import path
from pathlib import Path
import sys

class Metadata:
    __info: configparser.ConfigParser()

    @staticmethod
    def info() -> configparser.ConfigParser(): 
        if Metadata.__info is None:  # Read only once, lazy.
            print("inicialización de metadatos custom")
            Metadata.__info = configparser.ConfigParser()
            main_path = path.realpath(sys.argv[0]) if sys.argv[0] else None
            parent_path = Path(main_path).parent
            resources_path = path.join(parent_path, "resources/")
            conf_path = path.join(resources_path, 'metadata.cfg')
            print('ruta de fichero: '+conf_path)
            if path.exists(conf_path):
                Metadata.__info.read(conf_path)
                {section: print("Sección {0}: {1}".format(section, json.dumps(dict(Metadata.__info[section])))) for section in Metadata.__info.sections()}
                return Metadata.__info
            else:
                print('ruta no existe')


if __name__ == '__main__':
    print("prueba de metadata:")
    print(Metadata.info())
