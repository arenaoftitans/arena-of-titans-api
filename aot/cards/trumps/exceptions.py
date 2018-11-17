from ...game.exceptions import GameError


class TrumpError(GameError):
    pass


class GaugeTooLowToPlayTrump(TrumpError):
    pass


class MaxNumberAffectingTrumps(TrumpError):
    pass


class MaxNumberTrumpPlayed(TrumpError):
    pass


class NonExistantTrumpTarget(TrumpError):
    pass


class InvalidTargetType(TrumpError):
    pass


class TrumpHasNoEffect(TrumpError):
    pass
