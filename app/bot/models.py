import enum

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.schema import ForeignKey

from . import Base


class RoleType(enum.Enum):
    admin = "Admin"
    owner = "Owner"
    contributor = "Contributor"


class Pecha(Base):
    __tablename__ = "pecha"

    id = Column(String(7), primary_key=True)
    secret_key = Column(String(32))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    pecha_id = Column(String(7))
    role = Column(Enum(RoleType))
