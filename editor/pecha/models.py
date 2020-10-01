from editor.database import Column, PkModel, db


class Pecha(PkModel):
    __tablename__ = "pecha"

    secret_key = Column(db.String(32))
