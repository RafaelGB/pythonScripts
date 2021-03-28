from dependency_injector import containers, providers
# Server
from flask import make_response, jsonify, current_app, request
from flask.views import MethodView
# Own
from arq_server.services.protocols.physical.Common import arqCache
from arq_server.services.protocols.logical.NormalizeSelector import NormalizeSelector

class ApplicationsApi(MethodView):
    """
    API RESTful interfaz para llamadas a las diferentes aplicaciones
    """
    def __init__(self, view_name, *args, **kwargs):
        super(ApplicationsApi, self).__init__(*args, **kwargs)
        self.logger = current_app.logger
        self.view_name = view_name

    def get(self, app_name):
        """ app info """
        self.logger.info("View: '%s' - Peticion GET de la aplicación %s",self.view_name , app_name)
        return make_response(jsonify(app_name),200)

    def post(self, app_name):
        """ run app """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

    def put(self, app_name):
        """ substitute app info """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

    def patch(self, app_name):
        """ substitute app info """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

    def delete(self, app_name):
        """ delete app """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

class ArchitectureApi(MethodView):
    """
    API RESTful interfaz para la arquitectura
    """
    normalizer:NormalizeSelector

    def __init__(self, view_name, *args, **kwargs):
        self.normalizer=current_app.normalizer
        super(ArchitectureApi, self).__init__(*args, **kwargs)
        self.logger = current_app.logger
        self.view_name = view_name

    def get(self):
        """ app info """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

    def post(self):
        """ run app """
        form = self.__obtain_request()
        response_raw = self.normalizer.processInput(form)
        return make_response(jsonify(response_raw),200)

    def put(self):
        """ substitute app info """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

    def patch(self):
        """ substitute app info """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)

    def delete(self):
        """ delete app """
        return make_response(jsonify(arqCache.get('errors')["methodNotSupported"]), 400)
    
    def __obtain_request(self)->dict:
        rq = request.get_json()
        rq['metadata']=self.__metadata()
        return rq

    def __metadata(self)->dict:
        return {
            'protocol':'rest'
        }
