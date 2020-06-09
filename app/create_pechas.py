from uuid import uuid4

from bot import db_session, init_db
from bot.config import Config
from bot.models import Pecha

if __name__ == "__main__":
    init_db()
    start, end = (780, 785) if Config.DEBUG else (1, 1_000_000)
    for i in range(start, end):
        pecha_id = f"P{i:06}"
        pecha = Pecha(id=pecha_id, secret_key=uuid4().hex)
        print(f"added {pecha_id} - {pecha.secret_key}")
        db_session.add(pecha)
    db_session.commit()
