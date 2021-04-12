# Database
from typing import Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Sequence

from sqlalchemy.orm import relationship

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

# Systemfile
import hashlib
import os
import pickle
from datetime import date, datetime, timedelta

from sqlalchemy.sql.sqltypes import Boolean, Text

# Own
from arq_server.services.data_access.relational.DatabaseSQL import Base

"""
Ejemplos columnas
---
#id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
"""
class Token(Base):
    __tablename__ = 'arq_tokens'
    id = id = Column(Integer, Sequence('token_id_seq'), primary_key=True)
    client_id = Column(
        String(40), ForeignKey('arq_clients.client_id', ondelete='CASCADE'),
        nullable=False,
    )
    user_id = Column(
        Integer, ForeignKey('arq_users.id', ondelete='CASCADE')
    )
    user = relationship('User')
    client = relationship('Client')
    token_type = Column(String(40))
    access_token = Column(String(255))
    refresh_token = Column(String(255))
    expires = Column(DateTime)
    scope = Column(Text)

    def __init__(self, **kwargs):
        expires_in = kwargs.pop('expires_in', None)
        if expires_in is not None:
            self.expires = datetime.utcnow() + timedelta(seconds=expires_in)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @hybrid_property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []
