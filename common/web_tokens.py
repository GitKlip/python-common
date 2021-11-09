import base64
from json import dumps
from json import loads

import jwt


class UnexpectedWebTokenError(Exception):
    pass


class Userclaims:
    """ Access userclaims with lower snakecase properties.

    Example:
        userclaims = Userclaims(
            {
                "ClientId": 10,
                "Client": "ApiToApi",
                "ThreePlGuid": "REST-LOAD6",
                "ThreePlId": 5018,
                "UserLoginId": 708,
            }
        )
        userclaims.tpl_id
        userclaims.tpl_guid
        userclaims.user_login_id
        userclaims.client
        userclaims.client_id
        ...
    """
    KEYS = dict(
        tpl_id='ThreePlId',
        tpl_guid="ThreePlGuid",
        user_login_id="UserLoginId",
        client="Client",
        client_id="ClientId",
    )

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        """ Delegate to self.data after transforming key with KEYS. """
        data_key = self.KEYS.get(name, None)
        if data_key in self.data:
            return self.data[data_key]
        else:
            return super().__getattribute__(name)

    def encode(self):
        """ Returns a base64 encoded str of the data. """
        return base64.encodebytes(dumps(self.data).encode("utf-8")).decode("utf-8")


class TplCentralWebTokenCodec:
    """ Handle WMS Web token logic.

    Examples:
        # initialize
        codec = TplCentralWebTokenCodec(wms_secret_key_hex="<secret hex key>")

        # get userclaim info from request headers
        headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIU..."}
        codec.get_userclaims(headers)  # =>  {"ThreePlId": 5018, "UserLoginId":708, ...}

        # get the raw payload from the request headers
        # (note that the userclaim will still be base64 encoded)
        headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIU..."}
        codec.get_payload(headers)  # =>  {"exp": "1565288298", "aud": "http://localhost", ...}

        # get userclaim info from the token itself
        web_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIU..."
        codec.get_userclaims_from_token(web_token)  # =>  {"ThreePlId": 5018, "UserLoginId":708, ...}

        # get payload from the token itself
        web_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIU..."
        codec.get_payload_from_token(web_token)  # =>  {"exp": "1565288298", "aud": "http://localhost", ...}
    """
    AUTHORIZATION_HEADER_KEY = "Authorization"
    JWT_DECODE_OPTIONS = {"verify_exp": False, "verify_aud": False}
    ALLOWED_ALGORITHMS = ["HS256"]
    WEB_TOKEN_VALUE_STR = "Bearer {}"

    # does this work across all stages?
    USERCLAIMS_KEY = "http://www.3plCentral.com/AuthServer/claims/userinfo"

    def __init__(self, wms_secret_key_hex, userclaims_key=USERCLAIMS_KEY, verify_web_tokens=True):
        self.wms_secret_key = bytes.fromhex(wms_secret_key_hex)
        self.verify_web_tokens = verify_web_tokens
        self.userclaims_key = userclaims_key

    @classmethod
    def make_authorization_header(cls, web_token):
        """ Returns a dict suitable for merging with others to specify headers.

        Basically:
            return {AUTHORIZATION_HEADER_KEY: WEB_TOKEN_VALUE_STR.format(web_token)}
        """
        return {cls.AUTHORIZATION_HEADER_KEY: cls.WEB_TOKEN_VALUE_STR.format(web_token)}

    @staticmethod
    def get_web_token(headers):
        """ Given request headers (dict-like), returns the json web token.

        Args:
            headers (dict-like): Responds to __getitem__ and contains the
                AUTHORIZATION_HEADER_KEY and corresponding token. Typically,
                f"{AUTHORIZATION_HEADER_KEY}: Bearer <json_web_token>"

        Returns:
            (str): The json web token.
        """
        return headers[TplCentralWebTokenCodec.AUTHORIZATION_HEADER_KEY].split()[-1]

    def get_payload(self, headers):
        """ Returns the payload from an Authorization json web token

        Args:
            headers (dict-like): Responds to __getitem__ and contains the
                AUTHORIZATION_HEADER_KEY and corresponding token. Typically,
                f"{AUTHORIZATION_HEADER_KEY}: Bearer <json_web_token>"

        Returns:
            (dict): The payload as a python dict.

        """
        web_token = self.get_web_token(headers)
        return self.get_payload_from_token(web_token=web_token)

    def get_payload_from_token(self, web_token):
        """ Return the payload as a dict from the web_token.

        Args:
            web_token (str): An encoded json web token string.

        Returns:
            (dict): The payload as a dict.

        Raises:
            (jwt.exceptions.InvalidSignatureError): An invalid signature error if
                the signature is bad.
            (UnexpectedWebTokenError): On any other exception during token
                decoding.
        """
        try:
            return jwt.decode(
                web_token,
                key=self.wms_secret_key,
                algorithms=self.ALLOWED_ALGORITHMS,
                options=self.JWT_DECODE_OPTIONS,
                verify=self.verify_web_tokens,
            )
        except jwt.exceptions.InvalidSignatureError:
            # bare raise allows us to re-throw this exception as-is and catch
            # all others in the next except block
            raise
        except Exception as exc:
            raise UnexpectedWebTokenError(f"{type(exc)} {str(exc)}")

    def get_userclaims(self, headers):
        """ Returns the userclaims as a dict.

        Args:
        headers (dict-like): Responds to __getitem__ and contains the
            AUTHORIZATION_HEADER_KEY and corresponding token. Typically,
            f"{AUTHORIZATION_HEADER_KEY}: Bearer <json_web_token>"

        Returns:
            (Userclaims): A Userclaims object.
        """
        payload = self.get_payload(headers)
        return self.decode_userclaims(payload)

    def get_userclaims_from_token(self, web_token):
        """ Returns the userclaims as a dict.

        Args:
            web_token (str): An encoded json web token string.

        Returns:
        (dict): The userclaims as a python dict.
        """
        payload = self.get_payload_from_token(web_token)
        return self.decode_userclaims(payload)

    def decode_userclaims(self, web_token_payload):
        """ Returns the userclaim info as a Userclaims object.

        Args:
            web_token_payload (dict): The payload of a json web token.

        Returns:
            (Userclaims): The Userclaims object.
        """
        if self.userclaims_key not in web_token_payload:
            raise ValueError(
                f"userclaims_key {repr(self.userclaims_key)}\n"
                f"should be a key of the payload: {web_token_payload}\n"
                f"HINT: may need to pass in the right userclaims_key on creation."
            )
        base64_claims = web_token_payload[self.USERCLAIMS_KEY]
        decoded_bytes = base64.decodebytes(base64_claims.encode("utf-8"))
        data = loads(decoded_bytes.decode())
        return Userclaims(data)

    def make_web_token(self, payload):
        return jwt.encode(payload, self.wms_secret_key, algorithm='HS256').decode('utf-8')
