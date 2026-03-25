from flask import Blueprint, request, jsonify
from models import User
from database import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

auth_routes = Blueprint("auth", __name__)

bcrypt = Bcrypt()


@auth_routes.record_once
def setup(state):
    bcrypt.init_app(state.app)


# REGISTER
@auth_routes.route("/register", methods=["POST"])
def register():

    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 400

    hashed_pw = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    new_user = User(
        username=data["username"],
        email=data["email"],
        password=hashed_pw,
        role=data["role"]
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})


# LOGIN
@auth_routes.route("/login", methods=["POST"])
def login():

    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if user and bcrypt.check_password_hash(user.password, data["password"]):

        token = create_access_token(identity=str(user.id))

        return jsonify({
            "access_token": token,
            "role": user.role
        })

    return jsonify({"message": "Invalid credentials"}), 401