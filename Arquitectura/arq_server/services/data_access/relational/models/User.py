# Database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence

# Systemfile
import hashlib
import os

# Own
from arq_server.services.data_access.relational.models.CustomTypes import DictType
from arq_server.services.data_access.relational.DatabaseSQL import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    nickname = Column(String(50),unique=True)   
    password_hashed = Column(DictType())

    #below our user model, we will create our hashing functions

    def set_password(self, password):
        salt = os.urandom(32) # A new salt for this user
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        self.password_hashed = { # Store the salt and key
            'salt': salt.hex(),
            'key': key.hex()
        }

    def check_password(self, password):
        salt = bytes.fromhex(self.password_hashed['salt']) # Get the salt
        key = bytes.fromhex(self.password_hashed['key']) # Get the correct key
        key_to_check = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key == key_to_check
    
    def __repr__(self):
        return "name : "+self.name + \
               ",fullname : "+self.fullname + \
               ",nickname : "+self.nickname 