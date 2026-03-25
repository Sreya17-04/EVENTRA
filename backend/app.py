from flask import Flask
from flask_cors import CORS  
from database import db
from flask_jwt_extended import JWTManager
from routes import main_routes
from auth import auth_routes

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventra.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'this_is_a_very_secure_secret_key_123456'

# 🔥 ADD THESE 3 LINES
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"

# Initialize database
db.init_app(app)
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(main_routes)
app.register_blueprint(auth_routes)

@app.route("/")
def home():
    return "Backend is working successfully!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)