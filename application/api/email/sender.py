from application import config
from application.api.email.email import EmailClient


def send_email(to_email: str, content: str = None) -> bool:
    """Function for send email via custom client"""
    email = EmailClient(
        subject=config.SENDGRID_SUBJECT,
        from_email=config.SENDGRID_FROM_EMAIL,
        to_email=to_email,
        email_body=content
    )
    response = email.send()
    return response.status_code == 202
