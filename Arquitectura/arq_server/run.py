#!/bin/python -B
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import json
"""
# own
from arq_server.containers.ArqContainer import ArqContainer
from arq_decorators.arq_decorator import arq_decorator
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
@arq_decorator()
class Prueba():
    # declaro servicios propios del decorador para evitar que el lint indique error
    logger: object
    config: object
    def __init__(self):
        pass
    
    def prueba(self):
        self.logger.info(self.config.getProperty("base","filename_app_info"))

@arq_decorator()
class Prueba2():
    # declaro servicios propios del decorador para evitar que el lint indique error
    logger = None
    config = None
    def __init__(self):
        pass
    
    def prueba(self):
        self.logger.info(self.config.getProperty("base","filename_app_info"))
if __name__ == "__main__":
 
    # propiedad = ArqContainer.core_service().config_service().getProperty("base","filename_app_info")
    # ArqContainer.rest_service().prueba()
    prueba = Prueba()
    prueba.prueba()

    prueba2 = Prueba2()
    prueba2.prueba()
    #ArqContainer.protocols_service().rest_service().start_server()
   
    #app.run(debug=True)