from aot.utils import make_immutable

from .standard import STANDARD_CONFIG
from .test import TEST_CONFIG

GAME_CONFIGS = make_immutable({
    'test': TEST_CONFIG,
    'standard': STANDARD_CONFIG,
})
