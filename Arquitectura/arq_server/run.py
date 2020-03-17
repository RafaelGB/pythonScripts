#!/usr/bin/env python 
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import json
"""
import sys, os
import pathlib

# own
from arq_server.containers.ArqContainer import ArqContainer
from arq_decorators.arq_decorator import arq_decorator, ArqToolsTemplate
"""
-----------------------------------
            ENDPOINTS
-----------------------------------
"""
"""
@app.route('/applications/<string:appName>', methods=['GET'])
def returnOne(appName):
    if appName in apps:
        return jsonify(apps[appName])

@app.route('/applications/<string:appName>', methods=['POST'])
def addOne(appName):
    new_quark = request.get_json()
    print(new_quark)
    quarks.append(new_quark)
    return jsonify({'quarks' : quarks})

"""

class MiApp(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error
    
    def __init__(self,app_name, *args, **kwargs):
        self.app_name = app_name
        super().__init__(self.app_name,*args, **kwargs)
    
    def prueba(self):
        self.logger.info("utilizando log de la arquitectura en una clase. Propiedad '%s'",self.getProperty("mi.propiedad"))

if __name__ == "__main__":
 
    # propiedad = ArqContainer.core_service().config_service().getProperty("base","filename_app_info")
    # ArqContainer.rest_service().prueba()
    prueba = MiApp("app_pruebas")
    prueba.prueba()


    for (path, dirs, files) in os.walk(str(sys.path.append(os.path.dirname(os.path.abspath(__file__))))):
        prueba.logger.info(path)
        prueba.logger.info(dirs)
        prueba.logger.info(files)
        prueba.logger.info("----")
  
    #ArqContainer.protocols_service().rest_service().start_server()
   
    #app.run(debug=True)