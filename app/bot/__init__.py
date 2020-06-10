import os

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from bot.config import Config

app = Flask(__name__)

app.config.from_object(Config)

# Database setup
engine = create_engine(
    app.config["SQLALCHEMY_DATABASE_URI"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


from bot import bot_routes, maintainer_routes
