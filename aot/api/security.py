################################################################################
# Copyright (C) 2015-2018 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################

import hashlib
import hmac
from base64 import (
    b64decode,
    b64encode,
)

from ..config import config


class InvalidSignatureError(ValueError):
    pass


def encode(data):
    """Encode data in base 64 and append its b64 signature."""
    signature = sign(data)
    return b64encode(data) + b":" + b64encode(signature)


def sign(data):
    """Sign ``data`` with the sign_key from the config and return the signature.

    The result contains a b64 representation of the signature, a colon and a b64 representation
    of the data. This is meant to garante that the colon is present in neither of them.
    """
    secret = config["cache"]["sign_key"]
    return hmac.new(secret, msg=data, digestmod=hashlib.sha512).digest()


def decode(signed_data):
    """Return the decoded data from a signed data.

    raise:
        InvalidSignatureError: if the signature from signed_data in invalid.
    """
    try:
        encoded_data, encoded_signature = signed_data.rsplit(b":", 1)
        data = b64decode(encoded_data)
        signature = b64decode(encoded_signature)
        computed_signature = sign(data)
    except Exception:
        # Payload is not in the expected format, thus it is invalid.
        raise InvalidSignatureError

    if not hmac.compare_digest(signature, computed_signature):
        raise InvalidSignatureError

    return data
