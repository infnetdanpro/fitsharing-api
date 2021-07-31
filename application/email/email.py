class Response:
    status_code = 200

class Email:
    def __init__(self, sender_name: str, from_email: str, to_email: str, email_body: str):
        pass

    def send(self):
        response = Response()
        return response
