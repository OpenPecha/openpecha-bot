import enum
from uuid import uuid4

from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.schema import ForeignKey

from bot import Base


class RoleType(enum.Enum):
    maintainer = "Maintainer"
    contributor = "Contributor"
    user = "User"


class StatusType(enum.Enum):
    active = "Active"
    pending = "Pending"


class Pecha(Base):
    __tablename__ = "pecha"

    id = Column(String(7), primary_key=True)
    secret_key = Column(String(32), default=uuid4().hex)


class User(Base):
    __tablename__ = "users"

    id_ = Column(Integer, primary_key=True)
    github_access_token = Column(String(255))
    github_id = Column(Integer)
    github_login = Column(String(255))
    pecha_id = Column(ForeignKey("pecha.id"))
    role = Column(Enum(RoleType))
    status = Column(Enum(StatusType))

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token
