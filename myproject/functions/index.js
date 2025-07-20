const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

exports.callTrigger = functions.firestore
    .document("calls/trigger")
    .onWrite(async (change, context) => {
        const data = change.after.data();
        if (data) {
            const phoneNumber = data.phone_number;
            await admin.firestore().collection("call_events").doc("active").set({
                phone_number: phoneNumber,
                timestamp: admin.firestore.FieldValue.serverTimestamp()
            });
        }
    });
