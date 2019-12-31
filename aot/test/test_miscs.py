import pytest

from ..__main__ import main


@pytest.mark.timeout(1)
def test_no_startup_not_dev_no_cache_sign_key(monkeypatch):
    # Use a fake ENV, since it must raise for anything that is not development.
    monkeypatch.setenv("ENV", "mock")
    monkeypatch.setenv("CACHE_SIGN_KEY", "")

    with pytest.raises(EnvironmentError):
        main()
