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

"""
Ejemplos columnas
---
#id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
"""
class Client(Base):
    __tablename__ = 'arq_clients'
    # human readable name
    name = Column(String(50)) # Opcional
    # human readable description
    description = Column(String(400)) # Opcional

    client_id = Column(String(50),primary_key=True)   
    client_secret = Column(DictType())
    # public or confidential
    client_type = Column(String(20), default='public')

    _redirect_uris = Column(Text)
    _scope = Column(Text,default='read:all')

    @hybrid_property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

