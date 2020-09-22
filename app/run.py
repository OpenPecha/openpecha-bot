from .bot import app, init_db
from .bot.config import Config

init_db()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)
