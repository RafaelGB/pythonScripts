# Database
from typing import Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import Sequence

from sqlalchemy.orm import relationship

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

# Systemfile
import hashlib
import os
import pickle
from datetime import date

from sqlalchemy.sql.sqltypes import Boolean, Text

# Own
from arq_server.services.data_access.relational.models.CustomTypes import DictType
from arq_server.services.data_access.relational.DatabaseSQL import Base

class Grant(Base):
    __tablename__ = 'arq_grants'
    id = Column(Integer, Sequence('grant_id_seq'), primary_key=True)

    user_id = Column(
        Integer, ForeignKey('arq_users.id', ondelete='CASCADE')
    )
    user = relationship('User')

    client_id = Column(
        String(40), ForeignKey('arq_clients.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    code = Column(String(255), index=True, nullable=False)

    redirect_uri = Column(String(255))
    expires = Column(DateTime)

    _scopes = Column(Text)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
