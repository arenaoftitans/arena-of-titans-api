from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrumpPlayedInfos:
    """Mimics the attribute of a trump.

    This way we can use this instead when updating the gauge and creating the action.
    This is required to pass the proper information of ProxyTrumps.
    """

    name: str
    description: str
    cost: int
    duration: int
    must_target_player: bool
    color: Color  # noqa: F821 postponed annotation not supported.
    initiator: Player  # noqa: F821 postponed annotation not supported.
    is_power: bool = False


def return_trump_infos(func):
    def wrapper(trump, *args, **kwargs):
        func(trump, *args, **kwargs)
        return TrumpPlayedInfos(
            name=trump.name,
            description=trump.description,
            cost=trump.cost,
            duration=trump.duration,
            must_target_player=trump.must_target_player,
            color=trump.color,
            initiator=trump.initiator,
        )

    return wrapper
