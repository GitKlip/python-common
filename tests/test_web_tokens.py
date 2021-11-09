from unittest.mock import patch

import jwt
import pytest

from common.web_tokens import TplCentralWebTokenCodec
from common.web_tokens import Userclaims
from common.web_tokens import UnexpectedWebTokenError


class TestUserclaims:
    def setup_method(self, method):
        self.instance = Userclaims(
            {
                "ClientId": 10,
                "Client": "ApiToApi",
                "ThreePlGuid": "REST-LOAD6",
                "ThreePlId": 5018,
                "UserLoginId": 708,
            }
        )

    def test_accessing_attributes(self):
        """ Should allow standardized lowercase attribute names to access data. """
        expected = dict(
            client_id=10,
            client="ApiToApi",
            tpl_guid="REST-LOAD6",
            tpl_id=5018,
            user_login_id=708,
        )
        for key, val in expected.items():
            assert getattr(self.instance, key) == val

    def test_missing_attribute(self):
        """ Should return an AttributeError. """
        with pytest.raises(AttributeError):
            self.instance.not_a_legit_attribute


EXAMPLE_TOKEN = str(
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOiIxNTY1Mjg4Mjk4IiwiaXNzIjoiaHR0cDovL3N0YWdpbmcuc2VjdXJlLXd"
    "tcy5jb20vQXV0aFNlcnZlciIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3QiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzI"
    "wMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJzdXBlcmFkbWluIiwiaHR0cDovL3d3dy4zcGxDZW50cmFsLmNvbS9BdXRoU2VydmV"
    "yL2NsYWltcy91c2VyaW5mbyI6ImV5SkRiR2xsYm5SSlpDSTZNVEFzSWtOc2FXVnVkQ0k2SWtGd2FWUnZRWEJwSWl3aVZHaHlaV1ZRYkV"
    "kMWFXUWlPaUpTUlZOVUxVeFBRVVEySWl3aVZHaHlaV1ZRYkVsa0lqbzFNREU0TENKVmMyVnlURzluYVc1SlpDSTZOekE0ZlE9PSJ9."
    "-ijFBAwZADE-hspcxZAq75LPebEE4H_lLuK0n3_7Ll0"
)

DUMMY_SECRET_KEY_HEX = "aa14da3e8dd11259b2363f6c9071e056ca6a0643b6a62aec"


class TestTplCentralWebTokenCodec:
    """ Test the TplCentralWebTokenCodec. """

    PAYLOAD = {
        "exp": "1565288298",
        "iss": "http://staging.secure-wms.com/AuthServer",
        "aud": "http://localhost",
        "http://schemas.microsoft.com/ws/2008/06/identity/claims/role": "superadmin",
        "http://www.3plCentral.com/AuthServer/claims/userinfo": str(
            "eyJDbGllbnRJZCI6MTAsIkNsaWVudCI6IkFwaVRvQXBpIiwiVGhyZWVQbEd1aWQiOiJSRVNUL"
            "UxPQUQ2IiwiVGhyZWVQbElkIjo1MDE4LCJVc2VyTG9naW5JZCI6NzA4fQ=="
        ),
    }

    USERCLAIM_DATA = {
        "ClientId": 10,
        "Client": "ApiToApi",
        "ThreePlGuid": "REST-LOAD6",
        "ThreePlId": 5018,
        "UserLoginId": 708,
    }

    def setup_method(self, method):
        self.instance = TplCentralWebTokenCodec(wms_secret_key_hex=DUMMY_SECRET_KEY_HEX)

    def test_roundtrip_token(self):
        """ Should be able to decode a web token and then recode it.

        Note: Roundtrip with a token produced by the WMS system does not
        produce the same token, but it will produce equivalent payloads (which
        is all that matters).  Not sure why that is.  I produced this token
        after ensuring that was the case (not shown because don't want to
        reveal secret keys here).
        """
        original_payload = self.instance.get_payload_from_token(EXAMPLE_TOKEN)

        round_trip_token = self.instance.make_web_token(original_payload)
        roundtrip_payload = self.instance.get_payload_from_token(round_trip_token)
        assert original_payload == roundtrip_payload
        assert round_trip_token == EXAMPLE_TOKEN

    def test_get_payload_from_token(self):
        """ Should be able to decode a web token into a payload. """
        payload = self.instance.get_payload_from_token(EXAMPLE_TOKEN)
        assert payload == self.PAYLOAD

    def test_make_authorization_header(self):
        """ Should return a dict suitable for an authorization header. """
        response = TplCentralWebTokenCodec.make_authorization_header("mytoken")
        assert response == {'Authorization': 'Bearer mytoken'}

    def test_bad_signature(self):
        """ Should raise an jwt.exceptions.InvalidSignatureError with a bad signature. """
        bad_secret_key_hex = "cc14da3e8dd11259b2363f6c9071e056ca6a0643b6a62aec"
        instance = TplCentralWebTokenCodec(wms_secret_key_hex=bad_secret_key_hex)
        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            instance.get_payload_from_token(EXAMPLE_TOKEN)

    @patch('common.web_tokens.jwt.decode')
    def test_unexpected_error(self, mock_decode):
        """ Should raise an UnexpectedWebTokenError. """
        mock_decode.side_effect = RuntimeError("just some unexpected exception!")
        with pytest.raises(UnexpectedWebTokenError):
            self.instance.get_payload_from_token(EXAMPLE_TOKEN)

    def test_make_web_token(self):
        """ Should be able to create a token given a payload. """
        token = self.instance.make_web_token(self.PAYLOAD)
        assert token == EXAMPLE_TOKEN

    def test_decode_userclaims(self):
        """ Should return a functional Userclaims object. """
        payload = self.instance.get_payload_from_token(EXAMPLE_TOKEN)
        userclaims = self.instance.decode_userclaims(payload)
        self._assert_correct_userclaims(userclaims)

    def test_get_userclaims(self):
        """ Returns a Userclaims object. """
        headers = {"Authorization": f"Bearer {EXAMPLE_TOKEN}"}
        userclaims = self.instance.get_userclaims(headers=headers)
        self._assert_correct_userclaims(userclaims)

    def test_get_userclaims_from_token(self):
        """ Should return a Userclaims object. """
        userclaims = self.instance.get_userclaims_from_token(EXAMPLE_TOKEN)
        self._assert_correct_userclaims(userclaims)

    def test_bad_userclaims_key(self):
        """ Should raise a ValueError. """
        instance = TplCentralWebTokenCodec(wms_secret_key_hex=DUMMY_SECRET_KEY_HEX, userclaims_key='broken')
        payload = instance.get_payload_from_token(EXAMPLE_TOKEN)
        with pytest.raises(ValueError):
            instance.decode_userclaims(payload)

    def _assert_correct_userclaims(self, userclaims):
        assert userclaims.tpl_id == self.USERCLAIM_DATA['ThreePlId']
        assert userclaims.tpl_guid == self.USERCLAIM_DATA['ThreePlGuid']
