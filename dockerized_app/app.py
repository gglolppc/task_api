import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, g
from sqlalchemy import event
from routes.auth import auth
from routes.tasks import tasks
from flasgger import Swagger
from errors.handlers import register_error_handlers
from db.database import  Session

load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)
app.secret_key = os.getenv('SECRET_KEY')
app.register_blueprint(auth, url_prefix='/', strict_slashes=False)
app.register_blueprint(tasks, url_prefix='/tasks', strict_slashes=False)
# Base.metadata.create_all(engine)

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
    app.run(host='0.0.0.0', port=5000)