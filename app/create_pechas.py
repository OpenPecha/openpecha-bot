from bot import db_session, init_db
from bot.config import Config
from bot.models import Pecha

if __name__ == "__main__":
    init_db()
    end = 10 if Config.DEBUG else 1_000_000
    for i in range(1, end):
        pecha_id = f"P{i:06}"
        pecha = Pecha(id=pecha_id)
        print(f"added {pecha_id}")
        db_session.add(pecha)
    db_session.commit()
