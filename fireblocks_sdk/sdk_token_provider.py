import math
import secrets
import time
from hashlib import sha256

import jwt


class SdkTokenProvider(object):
    def __init__(self, private_key, api_key):
        self.private_key = private_key
        self.api_key = api_key

    def sign_jwt(self, path, content: str):
        timestamp = time.time()
        nonce = secrets.randbits(63)
        timestamp_secs = math.floor(timestamp)
        path = path.replace("[", "%5B")
        path = path.replace("]", "%5D")
        token = {
            "uri": path,
            "nonce": nonce,
            "iat": timestamp_secs,
            "exp": timestamp_secs + 55,
            "sub": self.api_key,
            "bodyHash": sha256(content.encode("utf-8")).hexdigest()
        }

        return jwt.encode(token, key=self.private_key, algorithm="RS256")
