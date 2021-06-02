# Database
from typing import Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import Sequence

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

# Systemfile
import hashlib
import os
import pickle
from datetime import date

from sqlalchemy.sql.sqltypes import Boolean, Text

# Own
from pyarq.arq_server.services.data_access.relational.models.CustomTypes import DictType
from pyarq.arq_server.services.data_access.relational.DatabaseSQL import Base

class User(Base):
    __tablename__ = 'arq_users'
    # human readable name
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), unique=True, index=True,
                         nullable=False)
    password = Column(DictType(),nullable=False)
    registered_on = Column(Date)

    def __init__(self,username,plain_password):
        # Optionals
        self.username=username
        # Normalized
        self.__set_password(plain_password)
        # Metadata
        self.registered_on = date.today()
    
    @hybrid_method
    def check_password(self, plain_password) -> Boolean:
        passBytes =  bytes.fromhex(self.password)
        passDict:Dict = pickle.loads(passBytes)
        salt = bytes.fromhex(passDict['salt']) # Get the salt
        key = bytes.fromhex(passDict['key']) # Get the correct key
        key_to_check = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return key == key_to_check
    
    def __set_password(self, plain_password):
        """
        Generamos un hash sobre la contraseña
        """
        salt = os.urandom(32) # A new salt for this user
        key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)

        passDict = { # Store the salt and key
            'salt': salt.hex(),
            'key': key.hex()
        }
        # Generamos hash del diccionario
        self.password = pickle.dumps(passDict).hex()
    
    def __repr__(self):
        return "username : "+self.username
