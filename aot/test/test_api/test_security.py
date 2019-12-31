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

from base64 import b64encode

import pytest

from ...api.security import InvalidSignatureError, decode, encode
from ...config import config


@pytest.fixture
def mocked_config(monkeypatch):
    monkeypatch.setenv("CACHE_SIGN_KEY", "secret-key")
    config.setup_config()
    return config


@pytest.fixture(autouse=True)
def mock_config(mocker, mocked_config):
    mocker.patch("aot.api.security.config", mocked_config)


@pytest.fixture
def signed_data():
    return b"c29tZS1kYXRh:J0b3ch+I7MkSXGtihguEjv3AAxDwgxQUBBoIoWr7SGTocK+rABXerCV4Z4Gtb1rCkvgqmMFnpfnGzwo2G6VLeg=="  # noqa


def test_sign(signed_data):
    data = b"some-data"
    encoded_data = encode(data)

    assert b":" in encoded_data
    assert signed_data == encoded_data


def test_decode(signed_data):
    data = decode(signed_data)

    assert data == b"some-data"


def test_decode_invalid_signature(signed_data):
    # We rely on the encode function
    _, signature = signed_data.rsplit(b":", 1)
    # We rely on b64encode to encode the new data to prevent base 64 decode errors.
    data = b64encode(b"some_bytes_to_change_signature")
    signed_data = data + b":" + signature

    with pytest.raises(InvalidSignatureError):
        decode(signed_data)


def test_decode_change_data(signed_data):
    signed_data = b"some_bytes_to_change_data" + signed_data

    with pytest.raises(InvalidSignatureError):
        decode(signed_data)


def test_decode_garbage():
    signed_data = b"some_bytes"

    with pytest.raises(InvalidSignatureError):
        decode(signed_data)
