from application import config
from application.email.email import Email
from application.email.template import Template


def send_email(to_email: str, template_name: str, context: dict = None) -> bool:
    if not context:
        context = {}

    template = Template(name=template_name, context=context)
    content: str = template.render()

    email = Email(
        from_email=config.SENDGRID_FROM_EMAIL,
        to_email=to_email,
        sender_name=config.SENDGRID_FROM_NAME,
        email_body=content
    )

    response = email.send()

    return response.status_code == 200
