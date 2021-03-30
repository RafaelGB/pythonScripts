# Security
import jwt
# system
import logging
import datetime
from typing import List
# Own
from arq_server.base.ArqErrors import ArqError
from arq_server.services.data_access.relational.models.User import User
from arq_server.services.CoreService import Base
from arq_server.services.CoreService import Configuration
from arq_server.services.data_access.relational.DatabaseSQL import DbSQL

class Security(Base):
    __logger: logging.Logger
    __config: Configuration
    __data: DbSQL

    def obtain_token(self,user, password,**kwargs):
        """
        Obtención de un token de seguridad en función del usuario
        ---
        Funcion preparada para llamada por instrucción
        """
        try:
            result:List[User]=self.__data.select_items_filtering_by(User,nickname=user)
            if (len(result)==0):
                raise Exception("Usuario incorrecto")
            user = result[0]
            if not user.check_password(password):
                raise Exception("Credenciales incorrectas")       

            return {
                'token' : self.__encode_auth_token(user.nickname,user.password_hashed)
                }
        except Exception as e:
            self.__logger.exception("Error obteniendo token del usuario %s",user)
            raise ArqError("Error obteniendo token:"+str(e),101)
    
    def __encode_auth_token(self,user_id,secret_key):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
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

    def __init__(self,core,data, *args, **kwargs):
        self.__init_services(core,data)

    def __init_services(self, core,data) -> None:
        # Servicio de logging
        self.__data = data.relational_tools().db_sql()
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()