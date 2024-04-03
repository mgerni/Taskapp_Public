import sendgrid
import config
from sendgrid.helpers.mail import Mail, Email, To, Content


def send_message(to, subject, body):
    sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)
    from_email = Email("taskapposrs@gmail.com")
    to_email = To(to)
    subject = subject
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    if config.IS_PROD:
        sg.client.mail.send.post(request_body=mail_json)
