import os
from dotenv import load_dotenv
from flask import Flask, g
from flask_app.routes.auth import auth
from flask_app.routes.tasks import tasks
from flask_app.errors.handlers import register_error_handlers
from flask_app.db.database import  Session
import logging
print("🚀 Running from:", os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("flask_app/logs/app.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

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


if __name__ == '__main__':
    app.run()
    # app.run(host='0.0.0.0', port=5000)


