# Database
from typing import Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import Sequence

# Systemfile
import hashlib
import os
import pickle
from datetime import date

# Own
from arq_server.services.data_access.relational.models.CustomTypes import DictType
from arq_server.services.data_access.relational.DatabaseSQL import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    fullname = Column(String(50)) # Opcional
    nickname = Column(String(50),unique=True)   
    password_hashed = Column(DictType())
    registered_on = Column(Date)

    def __init__(self,nickname,password,fullname=None):
        self.fullname=fullname
        self.nickname=nickname
        self.__set_password(password)
        self.registered_on = date.today()

    # Generamos un hash sobre la contraseña
    def __set_password(self, password):
        salt = os.urandom(32) # A new salt for this user
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

        passDict = { # Store the salt and key
            'salt': salt.hex(),
            'key': key.hex()
        }
        # Generamos hash del diccionario
        self.password_hashed = pickle.dumps(passDict).hex()

    def check_password(self, password):
        passBytes =  bytes.fromhex(self.password_hashed)
        passDict:Dict = pickle.loads(passBytes)
        salt = bytes.fromhex(passDict['salt']) # Get the salt
        key = bytes.fromhex(passDict['key']) # Get the correct key
        key_to_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key == key_to_check
    
    def __repr__(self):
        return "name : "+self.name + \
               "\tfullname : "+self.fullname + \
               "\tnickname : "+self.nickname 
