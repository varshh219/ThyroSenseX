import os
from dotenv import load_dotenv

load_dotenv()


def send_whatsapp_report(patient_phone, patient_name,
                         prediction, confidence):
    """Send WhatsApp message via Twilio."""

    # 🔴 Check env variables
    sid = os.getenv('TWILIO_SID')
    token = os.getenv('TWILIO_TOKEN')
    sender = os.getenv('TWILIO_WHATSAPP')

    if not sid or not token or not sender:
        print("❌ Twilio credentials missing (.env)")
        return False

    # 🔧 Fix confidence
    if confidence <= 1:
        confidence *= 100

    try:
        from twilio.rest import Client

        client = Client(sid, token)

        # 📱 Format phone (basic safety)
        phone = str(patient_phone).strip()
        if not phone.startswith("+"):
            phone = f"+91{phone}"  # default India

        message_body = (
            f"👋 Hello {patient_name},\n\n"
            f"🧠 *ThyroSenseX Scan Result*\n\n"
            f"🔍 Prediction: *{prediction}*\n"
            f"📊 Confidence: {confidence:.1f}%\n\n"
            f"📄 Your detailed report has been sent to your email.\n\n"
            f"⚠ Please consult a medical professional.\n\n"
            f"— ThyroSenseX"
        )

        message = client.messages.create(
            body=message_body,
            from_=sender,
            to=f"whatsapp:{phone}"
        )

        print(f"✅ WhatsApp sent → {message.sid}")
        return True

    except Exception as e:
        print("❌ WhatsApp error:", e)
        return False