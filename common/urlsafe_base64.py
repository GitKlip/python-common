"""
Python's default urlsafe encoding still leaves in '=' as padding which are
unsafe to use unencoded as URL params.  The functions below strip out the
padding and add it back in when needed.

Following after: https://gist.github.com/cameronmaske/f520903ade824e4c30ab
"""
import base64


def encode(value):
    utf8_encoded_value = value.encode("utf-8")
    encoded = base64.urlsafe_b64encode(utf8_encoded_value)
    base64_str = encoded.decode("utf-8")
    return base64_str.rstrip("=")


def decode(value):
    padding = 4 - (len(value) % 4)
    padded_value = value + ("=" * padding)
    decoded_bytestring = base64.urlsafe_b64decode(padded_value)
    return decoded_bytestring.decode("utf-8")
