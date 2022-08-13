import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


SENDGRID_API_KEY = 'REMOVED'


def send_message(to, subject, body):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email("taskapposrs@gmail.com")  # Change to your verified sender
    to_email = To(to)  # Change to your recipient
    subject = subject
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
