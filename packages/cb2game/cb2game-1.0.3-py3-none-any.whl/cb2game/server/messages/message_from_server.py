""" Defines message structure received from cb2game.server.  """

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

import dateutil.parser
from dataclasses_json import config
from marshmallow import fields
from mashumaro.mixins.json import DataClassJSONMixin

from cb2game.server.messages.action import Action
from cb2game.server.messages.feedback_questions import FeedbackQuestion
from cb2game.server.messages.google_auth import GoogleAuthConfirmation
from cb2game.server.messages.live_feedback import LiveFeedback
from cb2game.server.messages.map_update import MapUpdate
from cb2game.server.messages.menu_options import MenuOptions
from cb2game.server.messages.objective import ObjectiveMessage
from cb2game.server.messages.prop import Prop, PropUpdate
from cb2game.server.messages.replay_messages import ReplayResponse
from cb2game.server.messages.rooms import RoomManagementResponse
from cb2game.server.messages.scenario import ScenarioResponse
from cb2game.server.messages.sound_trigger import SoundTrigger
from cb2game.server.messages.state_sync import StateMachineTick, StateSync
from cb2game.server.messages.turn_state import TurnState
from cb2game.server.messages.tutorials import TutorialResponse
from cb2game.server.messages.user_info import UserInfo


class MessageType(Enum):
    ACTIONS = 0
    MAP_UPDATE = 1
    STATE_SYNC = 2
    ROOM_MANAGEMENT = 3
    OBJECTIVE = 4
    GAME_STATE = 5
    TUTORIAL_RESPONSE = 6
    PING = 7
    LIVE_FEEDBACK = 8
    PROP_UPDATE = 9
    STATE_MACHINE_TICK = 10
    GOOGLE_AUTH_CONFIRMATION = 11
    USER_INFO = 12
    # Triggers a prop spawn on the client
    PROP_SPAWN = 13
    # Used for signaling that a card set has been collected. The indicated props
    # will disappear on the client.
    PROP_DESPAWN = 14
    # Used for starting/stopping replays, relaying replay state.
    REPLAY_RESPONSE = 15
    # Used for starting/stopping/controlling scenario rooms.
    SCENARIO_RESPONSE = 16
    # Used for configuring a dynamic part of the main menu.
    MENU_OPTIONS = 17
    # Prompt the follower with feedback questions.
    SOUND_TRIGGER = 18
    FEEDBACK_QUESTION = 19


def ActionsFromServer(actions):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.ACTIONS,
        actions,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def MapUpdateFromServer(map_update):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.MAP_UPDATE,
        None,
        map_update,
        None,
        None,
        None,
        None,
        None,
    )


def StateSyncFromServer(state_sync):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.STATE_SYNC,
        None,
        None,
        state_sync,
        None,
        None,
        None,
        None,
    )


def RoomResponseFromServer(room_response):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.ROOM_MANAGEMENT,
        None,
        None,
        None,
        room_response,
        None,
        None,
        None,
    )


def ObjectivesFromServer(texts: List[ObjectiveMessage]):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.OBJECTIVE,
        None,
        None,
        None,
        None,
        texts,
        None,
        None,
    )


def GameStateFromServer(game_state):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.GAME_STATE,
        None,
        None,
        None,
        None,
        None,
        game_state,
        None,
    )


def TutorialResponseFromServer(tutorial_response):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.TUTORIAL_RESPONSE,
        None,
        None,
        None,
        None,
        None,
        None,
        tutorial_response,
    )


def PingMessageFromServer():
    return MessageFromServer(
        datetime.utcnow(), MessageType.PING, None, None, None, None, None, None, None
    )


def LiveFeedbackFromServer(feedback):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.LIVE_FEEDBACK,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        feedback,
    )


def PropUpdateFromServer(props: PropUpdate):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.PROP_UPDATE,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        props,
    )


def StateMachineTickFromServer(state_machine_tick):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.STATE_MACHINE_TICK,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        state_machine_tick,
    )


def GoogleAuthConfirmationFromServer(google_auth_confirmation):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.GOOGLE_AUTH_CONFIRMATION,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        google_auth_confirmation,
    )


def UserInfoFromServer(user_info):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.USER_INFO,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        user_info,
    )


def PropSpawnFromServer(prop):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.PROP_SPAWN,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        prop,
    )


def PropDespawnFromServer(props):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.PROP_DESPAWN,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        props,
    )


def ReplayResponseFromServer(replay_response):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.REPLAY_RESPONSE,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        replay_response,
    )


def ScenarioResponseFromServer(scenario_response):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.SCENARIO_RESPONSE,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        scenario_response,
    )


def MenuOptionsFromServer(menu_options):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.MENU_OPTIONS,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        menu_options,
    )


def SoundTriggerFromServer(sound_trigger):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.SOUND_TRIGGER,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        sound_trigger,
    )


def FeedbackQuestionFromServer(feedback_question):
    return MessageFromServer(
        datetime.utcnow(),
        MessageType.FEEDBACK_QUESTION,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        feedback_question,
    )


def ExcludeIfNone(value):
    return value is None


@dataclass(frozen=True)
class MessageFromServer(DataClassJSONMixin):
    transmit_time: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=dateutil.parser.isoparse,
            mm_field=fields.DateTime(format="iso"),
        )
    )
    type: MessageType
    actions: Optional[List[Action]] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    map_update: Optional[MapUpdate] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    state: Optional[StateSync] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    room_management_response: Optional[RoomManagementResponse] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    objectives: Optional[List[ObjectiveMessage]] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    turn_state: Optional[TurnState] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    tutorial_response: Optional[TutorialResponse] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    live_feedback: Optional[LiveFeedback] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    prop_update: Optional[PropUpdate] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    state_machine_tick: Optional[StateMachineTick] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    google_auth_confirmation: Optional[GoogleAuthConfirmation] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    user_info: Optional[UserInfo] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    prop_spawn: Optional[Prop] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    prop_despawn: Optional[List[Prop]] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    replay_response: Optional[ReplayResponse] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    scenario_response: Optional[ScenarioResponse] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    menu_options: Optional[MenuOptions] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    sound_trigger: Optional[SoundTrigger] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    feedback_question: Optional[FeedbackQuestion] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
