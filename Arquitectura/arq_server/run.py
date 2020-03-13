#!/bin/python -B

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import json

from flask import Flask
from flask import jsonify
from flask import request

from arq_server.containers.ArqContainer import ArqContainer

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
if __name__ == "__main__":
 
    # propiedad = ArqContainer.core_service().config_service().getProperty("base","filename_app_info")
    # ArqContainer.rest_service().prueba()
    ArqContainer.rest_service().start_server()
   
    #app.run(debug=True)