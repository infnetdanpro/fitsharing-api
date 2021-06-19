import string
from random import choice


base = list(string.ascii_lowercase + string.digits + '!#$%')


def generate_code(length: int = 10) -> str:
    code = ''

    while True:
        if len(code) == length:
            break

        code += choice(base)

    return code
