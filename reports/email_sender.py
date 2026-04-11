import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from dotenv               import load_dotenv
load_dotenv()

def send_report_email(patient_email, patient_name,
                      pdf_path, prediction):
    """Send PDF report to patient via Gmail SMTP."""
    sender   = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEMultipart()
    msg['From']    = sender
    msg['To']      = patient_email
    msg['Subject'] = f'ThyroSenseX Diagnostic Report — {patient_name}'

    body = f'''
Dear {patient_name},

Please find attached your ThyroSenseX diagnostic report.
Prediction: {prediction}

Note: This is a screening report only.
Please consult a licensed medical professional for confirmation.

Regards,
ThyroSenseX AI Diagnostic System
'''
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    with open(pdf_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
        f'attachment; filename={os.path.basename(pdf_path)}')
    msg.attach(part)

    # Send via Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)
    print(f'Email sent to {patient_email}')
    return True
