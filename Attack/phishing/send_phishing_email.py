import smtplib
from email.message import EmailMessage

# Phishing website link
phishing_link = "http://localhost:5000"

# Email configuration
sender_email = "group8cw@gmail.com"
receiver_email = "elec0138@outlook.com"
app_password = "mxzzhfsnlfbhcsox"

# Email content
msg = EmailMessage()
msg["Subject"] = "【Notice】New File Upload Notification - Action Required"
msg["From"] = sender_email
msg["To"] = receiver_email

body = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h3>Hi there,</h3>

    <p>You have received a <strong>new secure file</strong> via File Upload App.</p>

    <p>To view or download the file, please verify your account by clicking the link below:</p>

    <p>
        <a href="{phishing_link}" style="color: #d9534f; font-weight: bold;">
            Access File Now
        </a>
    </p>

    <p>If you did not expect this file or do not recognize the sender, please ignore this message.</p>

    <br>
    <p>Regards,<br>
    File Upload App Security Team</p>
</body>
</html>
"""


msg.add_alternative(body, subtype='html')

# Send email
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)
        print("Email sent successfully!")



except smtplib.SMTPAuthenticationError as e:
    print("Login failed, please check if your email and App Password are correct.")
    print("Error message:", e)
except Exception as e:
    print("Sending failed. An unknown error occurred：", e)
