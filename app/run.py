from bot import app, init_db
from bot.config import Config

if __name__ == "__main__":
    init_db()
    app.run(port="8000", debug=Config.DEBUG)
