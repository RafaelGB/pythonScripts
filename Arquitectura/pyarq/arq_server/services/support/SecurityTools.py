# Security
import jwt
# system
import logging
import base64
import datetime
from typing import List
# Own
from pyarq_core.ArqErrors import ArqError
from pyarq.arq_server.services.data_access.relational.models.User import User
from pyarq_core.Base import Base
from pyarq_core.Config import Configuration
from pyarq.arq_server.services.data_access.relational.DatabaseSQL import DbSQL

class Security(Base):
    __logger: logging.Logger
    __config: Configuration
    __data: DbSQL

    def obtain_token(self,**kwargs):
        """
        Obtención de un token de seguridad en función del usuario
        ---
        Funcion preparada para llamada por instrucción
        """
        try:
            if 'Authorization' not in kwargs:
                raise Exception("Petición sin autorización")

            authorization:str = kwargs['Authorization']
            username,password = self.__decode_basic_auth(authorization)
            user = self.__obtainUser(username)
            if not user.check_password(password):
                raise Exception("Credenciales incorrectas")       

            return {
                'token' : self.__encode_auth_token(user.username,user.password)
                }
        except Exception as e:
            self.__logger.exception("Error obteniendo token del usuario %s",user)
            raise ArqError("Error obteniendo token:"+str(e))
    
    def validate_token(self,token,**kwargs):
        """
        Valida el token activo
        ---
        Funcion preparada para llamada por instrucción
        """
        try:
            payload = self.__obtainPayload(token)
            if 'sub' not in payload:
                raise ArqError("El token no tiene asociado ningun usuario")
            user = self.__obtainUser(payload['sub'])
            self.__validate_auth_token(token,user.password)
        except ArqError as arqE:
            # Excepciones ya controladas
            raise arqE

    def __obtainPayload(self,token):
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            raise ArqError("Ha habido un problema obteniendo el payload del token:"+str(e))

    def __decode_basic_auth(self,authorization:str):
        auth:str = authorization.split(" ")[1]
        message_bytes = base64.b64decode(auth)
        plain_auth = message_bytes.decode('utf8')
        result = plain_auth.split(':')
        return result[0],result[1]

    def __obtainUser(self,username):
        """
        Devuelve el usuario en función de su username
        ---
        En caso de no encontrarse, se lanza una excepción
        """
        user:User=self.__data.select_unique_item_filtering_by(User,username=username)
        if user is None:
            raise Exception("Usuario no encontrado")
        return user
    
    def __encode_auth_token(self,user_id,secret_key):
        """
        Generates the Auth Token
        :return: string
        """
        filterConf="jwt.token.ttl."
        def callback(elem): return elem.startswith(filterConf)
        ttl_token_conf = self.__config.getFilteredGroupOfProperties("security",callback)
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    days=int(ttl_token_conf[filterConf+'days']),
                    hours=int(ttl_token_conf[filterConf+'hours']),
                    minutes=int(ttl_token_conf[filterConf+'minutes']),
                    seconds=int(ttl_token_conf[filterConf+'seconds'])
                    ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                secret_key,
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    def __validate_auth_token(self,token,secret_key):
        """
        Valida el token activo
        """
        try:
            payload = jwt.decode(token, secret_key,algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError as expired:
            raise ArqError('El token ya ha expirado. Requiere renovación'+str(expired))
        except jwt.InvalidTokenError as invalid:
            raise ArqError('Credenciales incorrectas para el token'+str(invalid))


    def __init__(self,core,data, *args, **kwargs):
        self.__init_services(core,data)

    def __init_services(self, core,data) -> None:
        # Servicio de logging
        self.__data = data.relational_tools().db_sql()
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()