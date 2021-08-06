import sendgrid

from application import config
from sendgrid.helpers.mail import *


class EmailClient:
    def __init__(self, subject: str, from_email: str, to_email: str, email_body: str):
        self.subject = subject
        self.from_email = from_email
        self.to_email = to_email
        self.email_body = email_body

        self.sg = sendgrid.SendGridAPIClient(api_key=config.SENDGRID_API_KEY)

    def send(self):
        from_email = Email(self.from_email)
        to_email = To(self.to_email)
        subject = self.subject
        content = Content("text/plain", self.email_body)
        mail = Mail(from_email, to_email, subject, content)
        response = self.sg.client.mail.send.post(request_body=mail.get())
        return response
