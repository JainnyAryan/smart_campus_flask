from flask import Flask, Response, request, jsonify
from config import Config
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from flask_cors import CORS
from utils.decorators import protected_route

import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Azure Key Vault setup
keyVaultName = "googlecreds"
KVUri = f"https://{keyVaultName}.vault.azure.net"

# Authenticate and connect to Key Vault
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

# Retrieve the secret
retrieved_secret = client.get_secret('googleCredsJson')

# Write the secret to a temporary file for Firebase Admin SDK
temp_file_path = "/tmp/google_creds.json"
with open(temp_file_path, "w") as f:
    f.write(retrieved_secret.value)

# Firebase setup
cred = credentials.Certificate(temp_file_path)
firebase_admin.initialize_app(cred)

# Initialize SocketIO
# socketio = SocketIO(app, cors_allowed_origins="*")

# Register Blueprints
from controllers.user_controller import user_bp
from controllers.driver_controller import driver_bp
from controllers.student_controller import student_bp
from controllers.wallet_controller import wallet_bp
from controllers.shuttle_controller import shuttle_bp
from controllers.face_controller import face_bp
from controllers.history_controller import history_bp

app.register_blueprint(user_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(student_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(shuttle_bp)
app.register_blueprint(face_bp)
app.register_blueprint(history_bp)


@app.route("/", methods=['GET'])
def hello():
    return "Hello World"


@app.route("/protected", methods=['GET'])
@protected_route
def protected():
    return jsonify({"user": request.user}), 200


if __name__ == '__main__':
    app.run()
    # socketio.run(app, host="0.0.0.0", port=6001, debug=True)