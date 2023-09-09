from dataclasses import dataclass
from enum import IntEnum

from mashumaro.mixins.json import DataClassJSONMixin


class LobbyType(IntEnum):
    NONE = 0
    MTURK = 1
    OPEN = 2
    GOOGLE = 3
    FOLLOWER_PILOT = 4
    REPLAY = 5
    SCENARIO = 6
    GOOGLE_LEADER = 7


def IsMturkLobby(lobby_type):
    return lobby_type in [LobbyType.MTURK, LobbyType.FOLLOWER_PILOT]


def IsGoogleLobby(lobby_type):
    return lobby_type in [LobbyType.GOOGLE, LobbyType.GOOGLE_LEADER]


def LobbyTypeFromString(data):
    if data == "LobbyType.MTURK":
        return LobbyType.MTURK
    if data == "LobbyType.OPEN":
        return LobbyType.OPEN
    if data == "LobbyType.GOOGLE":
        return LobbyType.GOOGLE
    if data == "LobbyType.FOLLOWER_PILOT":
        return LobbyType.FOLLOWER_PILOT
    if data == "LobbyType.REPLAY":
        return LobbyType.REPLAY
    if data == "LobbyType.SCENARIO":
        return LobbyType.SCENARIO
    if data == "LobbyType.GOOGLE_LEADER":
        return LobbyType.GOOGLE_LEADER
    return LobbyType.NONE


@dataclass
class LobbyInfo(DataClassJSONMixin):
    name: str
    type: LobbyType
    comment: str = ""
    # The maximum number of games that can be created in this lobby.
    game_capacity: int = 40
    # To disable sound, just set this to 0.0
    sound_clip_volume: float = 1.0
    # After each instruction, prompt the follower with questions.
    follower_feedback_questions: bool = False
    # From the follower's POV, the cards are standing and facing the follower.
    cards_face_follower: bool = False
    # For lobbies which use experience to match players, this is the percentage
    # of times when the player will be matched randomly instead of by
    # experience.
    ranked_matchmaking_randomness: float = 0.0
    live_feedback_enabled: bool = True
    delayed_feedback_enabled: bool = True
    # Replay lobbies only. Useful for demoing at conferences and such.
    is_demo_lobby: bool = False
    # The bottom-left UI element won't show the number of moves remaining.
    hide_moves_remaining: bool = False
    # If this is enabled, then the game will require a button press (P) to
    # select cards. Otherwise, cards will not be selected when a player walks
    # over them.
    select_requires_button_press: bool = False
    card_covers: bool = False
