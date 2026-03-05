import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json

# Try to read from environment variable first (for Render)
cred_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

if cred_json:
    # Running on Render - read from env variable
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
else:
    # Running locally - read from file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_dir, "serviceAccountKey.json")
    cred = credentials.Certificate(key_path)

firebase_admin.initialize_app(cred)

db = firestore.client()

def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except:
        return None