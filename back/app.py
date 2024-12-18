from flask import Flask
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from routes.auth_routes import auth_blueprint
from routes.user_routes import user_blueprint
from routes.admin_routes import admin_blueprint
from routes.lesson_routes import lesson_blueprint
from routes.course_routes import course_blueprint
from routes.payment_routes import payment_blueprint
from routes.chat_routes import chat_blueprint
# from routes.upload_routes import upload_blueprint
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:3000"])

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.register_blueprint(lesson_blueprint, url_prefix="/lesson")
app.register_blueprint(course_blueprint, url_prefix="/course")
app.register_blueprint(payment_blueprint, url_prefix="/payment")
app.register_blueprint(chat_blueprint, url_prefix="/chat")

# app.register_blueprint(upload_blueprint, url_prefix='/upload')

if __name__ == "__main__":
    app.run(debug=True)