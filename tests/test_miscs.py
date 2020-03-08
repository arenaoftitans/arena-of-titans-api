#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

import pytest

from aot.__main__ import main


@pytest.mark.timeout(1)
def test_no_startup_not_dev_no_cache_sign_key(monkeypatch):
    # Use a fake ENV, since it must raise for anything that is not development.
    monkeypatch.setenv("ENV", "mock")
    monkeypatch.setenv("CACHE_SIGN_KEY", "")

    with pytest.raises(EnvironmentError):
        main()
