import jwt
import json
import time
import math
from hashlib import sha256

class SdkTokenProvider(object):
    def __init__(self, private_key, api_key):
        self.private_key = private_key
        self.api_key = api_key

    def sign_jwt(self, path, body_json=""):
        timestamp = time.time()
        timestamp_millisecs = int(timestamp * 1000)
        timestamp_secs = math.floor(timestamp)

        token = {
            "uri": path,
            "nonce": timestamp_millisecs,
            "iat": timestamp_secs,
            "exp": timestamp_secs + 55, 
            "sub": self.api_key,
            "bodyHash": sha256(json.dumps(body_json).encode("utf-8")).hexdigest()
        }

        return jwt.encode(token, key=self.private_key, algorithm="RS256").decode('utf-8')
