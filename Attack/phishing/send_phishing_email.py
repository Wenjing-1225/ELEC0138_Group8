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
msg["Subject"] = "【Notice】Abnormal account login, please verify your identity immediately"
msg["From"] = sender_email
msg["To"] = receiver_email

# HTML content
body = f"""
<html>
<body>
<p>Dear Customer,</p>

<p>We have detected <strong>unusual login activity</strong> in your account.<br>
To ensure the security of your account, please click the following link to verify:</p>

<p><a href="{phishing_link}">{phishing_link}</a></p>

<p>If you did not initiate this login, please ignore this email.</p>

<p>Best regards,<br>
Bank Security Department</p>
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
