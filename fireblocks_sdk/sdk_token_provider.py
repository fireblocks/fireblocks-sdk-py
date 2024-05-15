import jwt
import json
import time
import math
import secrets
from hashlib import sha256


class SdkTokenProvider:
    def __init__(self, private_key, api_key, seconds_jwt_exp):
        self.private_key = private_key
        self.api_key = api_key
        self.seconds_jwt_exp = seconds_jwt_exp

    def sign_jwt(self, path, body_json=""):
        timestamp = time.time()
        nonce = secrets.randbits(63)
        timestamp_secs = math.floor(timestamp)
        path= path.replace("[", "%5B")
        path= path.replace("]", "%5D")
        token = {
            "uri": path,
            "nonce": nonce,
            "iat": timestamp_secs,
            "exp": timestamp_secs + self.seconds_jwt_exp, 
            "sub": self.api_key,
            "bodyHash": sha256(json.dumps(body_json).encode("utf-8")).hexdigest()
        }

        return jwt.encode(token, key=self.private_key, algorithm="RS256")
