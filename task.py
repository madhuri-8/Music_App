from celery import shared_task
import time
from mailer import sendMail


'''@shared_task()
def daily_reminder(message):
    return message'''

@shared_task()
def send_email(email_id):
    
    sendMail(email_id,"Swara","<b style='color:red'>We haven't seen you for a day. Visit us! </b>")

@shared_task()

def send_report(email_id,subject,message):
    sendMail(email_id,subject,message)

    
if __name__ == '__main__':
    celery.start()