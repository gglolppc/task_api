import os
from dotenv import load_dotenv
from flask import Flask, g
from flask_app.routes.auth import auth
from flask_app.routes.tasks import tasks
from flask_app.errors.handlers import register_error_handlers

import logging
from flask_app.db.database import Base, engine

LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
        logging.StreamHandler()
    ]
)

load_dotenv()
print("DATABASE_URL =", os.getenv('DATABASE_URL'))
if not os.getenv('DATABASE_URL'):
    raise RuntimeError("DATABASE_URL is not set!")
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.register_blueprint(auth, url_prefix='/', strict_slashes=False)
app.register_blueprint(tasks, url_prefix='/tasks', strict_slashes=False)


@app.before_request
def before_request():
    g.db = Session()
@app.teardown_request
def close_session(exception=None):
    db = getattr(g, 'db', None)
    if db is not None:
        if exception:
            db.rollback()
        else:
            db.commit()
        db.close()
register_error_handlers(app)

with engine.begin() as connection:
    Base.metadata.create_all(bind=connection)

if __name__ == '__main__':
    app.run()
    # app.run(host='0.0.0.0', port=5000)


