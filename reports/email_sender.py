import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()


def send_report_email(patient_email, patient_name, pdf_path, prediction):
    """Send PDF report via Gmail SMTP."""

    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')

    # 🔴 Check credentials
    if not sender or not password:
        print("Email credentials missing (.env)")
        return False

    if not os.path.exists(pdf_path):
        print("PDF not found:", pdf_path)
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = patient_email
        msg['Subject'] = f"ThyroSenseX Report — {patient_name}"

        # 🎨 HTML Email Body (better than plain text)
        body = f"""
        <html>
        <body style="font-family:Arial; color:#333;">
            <h2 style="color:#1f6feb;">ThyroSenseX Diagnostic Report</h2>

            <p>Dear <b>{patient_name}</b>,</p>

            <p>Your thyroid screening result is ready.</p>

            <p><b>Prediction:</b> {prediction}</p>

            <p>Please find the attached PDF report for full details.</p>

            <hr>

            <p style="font-size:12px; color:#777;">
                ⚠ This is an AI-based screening tool and not a medical diagnosis.
                Please consult a certified doctor.
            </p>

            <p>Regards,<br><b>ThyroSenseX Team</b></p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # 📄 Attach PDF
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{os.path.basename(pdf_path)}"'
        )
        msg.attach(part)

        # 📡 Send Email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)

        print(f"✅ Email sent to {patient_email}")
        return True

    except Exception as e:
        print("❌ Email sending failed:", e)
        return False