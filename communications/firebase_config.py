import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:
    cred = credentials.Certificate("communications/firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fir-56219-default-rtdb.firebaseio.com'  # replace this
    })



