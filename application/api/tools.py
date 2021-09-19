import typing
from base64 import b64encode
from functools import cache
from io import BytesIO

import qrcode


@cache
def _get_qrcode_cachend(*args, **kwargs):
    return _get_qrcode(*args, **kwargs)


def _get_qrcode(content: typing.Any) -> str:
    """Generate QR-code object as base64 string"""
    img = qrcode.make(str(content))
    output: BytesIO = BytesIO()
    img.save(output)
    string = b64encode(output.getvalue())
    return string.decode('utf-8')


def get_qrcode(content: typing.Any, cached: bool = True) -> str:
    if cached:
        return _get_qrcode_cachend(content=content)
    return _get_qrcode(content=content)
