
from common.urlsafe_base64 import encode
from common.urlsafe_base64 import decode


class TestUrlSafeBase64:

    UNENCODED_STRING = "My string that needs encoding"
    BASE64_STRING = "TXkgc3RyaW5nIHRoYXQgbmVlZHMgZW5jb2Rpbmc"

    def test_encode(self):
        """ Should encode and return a string without '=' padding. """
        base64_str = encode(self.UNENCODED_STRING)
        assert isinstance(base64_str, str)
        assert '=' not in base64_str
        # frozen
        assert base64_str == self.BASE64_STRING

    def test_decode(self):
        value = decode(self.BASE64_STRING)
        assert isinstance(value, str)
        assert value == self.UNENCODED_STRING
