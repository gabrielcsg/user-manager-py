from flask import Flask, jsonify, request
from database import db
from flask_login import LoginManager, current_user, login_user
from models.user import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"  # dev

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return jsonify({"message": "authentication successful"})

    return jsonify({"message": "invalid credentials"}), 400


@app.route("/", methods=["GET"])
def hello_world():
    return "hello world"


if __name__ == "__main__":
    app.run(debug=True)
