import string
from random import choice


def generate_code(length: int = 10, case: str = 'base') -> str:
    """Generate string, using for reset_code and confirm code"""
    cases = {
        'base': list(string.ascii_lowercase + string.digits + '!#$%'),
        'letters': list(string.ascii_lowercase),
        'letters+numbers': list(string.ascii_lowercase + string.digits)
    }
    code = ''

    while True:
        if len(code) == length:
            return code
        code += choice(cases[case])
