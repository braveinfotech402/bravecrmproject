import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("myapp/firebase/firebase-key.json")
firebase_admin.initialize_app(cred)

def send_fcm_notification(token: str, phone: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title="make a Call",
            body=phone,
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        print(f"Sent FCM message: {response}")
        return True
    except Exception as e:
        print(f"FCM send error: {e}")
        return False
    


