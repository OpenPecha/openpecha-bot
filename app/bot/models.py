from uuid import uuid4

from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import ForeignKey

from bot import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    github_access_token = Column(String(255))
    github_id = Column(Integer)
    github_login = Column(String(255))

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


class Pecha(Base):
    __tablename__ = "pecha"

    id = Column(Integer, primary_key=True)
    op_id = Column(String(8))
    secret_key = Column(String(32), default=uuid4().hex)


class Maintainer(Base):
    __tablename__ = "maintainers"

    id = Column(Integer, primary_key=True)
    username = Column(String(120))
    pecha = Column(ForeignKey("pecha.id"))
