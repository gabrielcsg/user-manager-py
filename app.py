from flask import Flask
from database import db
from models.user import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"  # dev

db.init_app(app)


@app.route("/", methods=["GET"])
def hello_world():
    return "hello world"


if __name__ == "__main__":
    app.run(debug=True)
