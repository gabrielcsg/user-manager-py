import bcrypt
from flask import Flask, jsonify, request
from database import db
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from models.user import User

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin123@127.0.0.1:3306/flask-crud"  # docker

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

        if user and bcrypt.checkpw(
                str.encode(password),
                str.encode(user.password)):
            login_user(user)
            return jsonify({"message": "authentication successful"})

    return jsonify({"message": "invalid credentials"}), 401


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "successful logout"})


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        password_hashed = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        new_user = User(
            username=username,
            password=password_hashed,
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "user created successful"}), 201

    return jsonify({"message": "missing attributes"}), 400


@app.route("/users/<int:user_id>", methods=["GET"])
@login_required
def read_user(user_id):
    user = User.query.get(user_id)

    if user:
        return jsonify({"username": user.username})

    return jsonify({"message": "user not found"}), 404


@app.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    user = User.query.get(user_id)

    if user_id != current_user.id and current_user.role == "user":
        return jsonify({"message": "operation not permitted"}), 403

    if not user:
        return jsonify({"message": "user not found"}), 404

    data = request.json
    password = data.get("password")

    if password:
        user.password = password
        db.session.commit()
        return jsonify({"message": "user updated successful"}), 200

    return jsonify({"message": "missing attributes"}), 400


@app.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if current_user.role != "admin":
        return jsonify({"message": "operation not permitted"}), 403

    if user_id == current_user.id:
        return jsonify({"message": "deletion not permitted"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "user deleted successful"})

    return jsonify({"message": "user not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
