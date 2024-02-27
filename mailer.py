from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
import smtplib 




SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = "mad@gmail.com"
SENDER_PASSWORD = ""


'''def get_all_email_ids():
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    email_ids = [person.email for person in People.query.filter(People.visited_time < twenty_four_hours_ago).all()]
    return email_ids'''


def sendMail(receiver, subject, message):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = receiver
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "html"))
    
    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)

    s.send_message(msg)
    s.quit()
    return True

def sendMailer(receiver, subject, message, content='html', attachment=None):
    msg = MIMEMultipart()
    msg['To'] = receiver
    msg['From'] = SENDER_ADDRESS
    msg['Subject'] = subject

    msg.attach(MIMEText(message, "html"))
    
    if attachment:
        with open(attachment, "rb") as a:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(a.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={attachment}")
        msg.attach(part)  

    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)

    s.send_message(msg)
    print("Email sent successfully")
    s.quit()
    return True

# Example: Sending a hello message to all users
#users = get_all_email_ids()


    