import os
from dotenv import load_dotenv
load_dotenv()

def send_whatsapp_report(patient_phone, patient_name,
                         prediction, confidence):
    """Send WhatsApp message via Twilio."""
    try:
        from twilio.rest import Client
        client = Client(
            os.getenv('TWILIO_SID'),
            os.getenv('TWILIO_TOKEN')
        )
        message = client.messages.create(
            body=(
                f'Hello {patient_name},\n\n'
                f'Your ThyroSenseX scan result:\n'
                f'Prediction: *{prediction}*\n'
                f'Confidence: {confidence:.1f}%\n\n'
                f'Your full PDF report has been emailed to you.\n'
                f'Please consult a doctor for confirmation.\n\n'
                f'ThyroSenseX AI Diagnostic System'
            ),
            from_=os.getenv('TWILIO_WHATSAPP'),
            to=f'whatsapp:+91{patient_phone}'
        )
        print(f'WhatsApp sent: {message.sid}')
        return True
    except Exception as e:
        print(f'WhatsApp error: {e}')
        return False