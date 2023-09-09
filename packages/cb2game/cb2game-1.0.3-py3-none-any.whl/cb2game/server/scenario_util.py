""" Utilities used for working with scenarios and game data."""
import logging
from datetime import datetime, timedelta

import orjson

import cb2game.server.messages.action as action_module
import cb2game.server.messages.objective as objective
import cb2game.server.schemas.game as game_db
from cb2game.pyclient.game_endpoint import GameState
from cb2game.server.actor import Actor
from cb2game.server.card import Card
from cb2game.server.messages.map_update import MapUpdate
from cb2game.server.messages.prop import PropType, PropUpdate
from cb2game.server.messages.rooms import Role
from cb2game.server.messages.scenario import Scenario
from cb2game.server.messages.state_sync import StateSync
from cb2game.server.messages.turn_state import TurnState, TurnUpdate
from cb2game.server.schemas.event import Event, EventOrigin, EventType
from cb2game.server.schemas.util import InitialState

logger = logging.getLogger(__name__)

LEADER_MOVES_PER_TURN = 5
FOLLOWER_MOVES_PER_TURN = 10
LEADER_SECONDS_PER_TURN = 50
FOLLOWER_SECONDS_PER_TURN = 15


def TurnDuration(role):
    return (
        timedelta(seconds=LEADER_SECONDS_PER_TURN)
        if role == Role.LEADER
        else timedelta(seconds=FOLLOWER_SECONDS_PER_TURN)
    )


def ReconstructScenarioFromEvent(event_uuid: str) -> Scenario:
    """Looks up a given event in the database.

    Returns:
        A tuple of (Scenario, None) if the scenario was found, or (None, error_message) if not.

    """
    # Get the event matching this UUID, make sure it's unique.
    event_query = (
        Event.select().join(game_db.Game).where(Event.id == event_uuid).limit(1)
    )
    if event_query.count() != 1:
        return (
            None,
            f"1 Event {event_uuid} not found. ({event_query.count()} found)",
        )
    event = event_query.get()
    game_record = event.game

    # Get all events from the same game that happened before this event.
    game_events = (
        Event.select()
        .where(Event.game == game_record, Event.server_time <= event.server_time)
        .order_by(Event.server_time)
    )

    # Get the game map.
    map_event = game_events.where(Event.type == EventType.MAP_UPDATE).get()
    map_update = MapUpdate.from_json(map_event.data)

    card_events = game_events.where(
        Event.type
        << [
            EventType.CARD_SET,
            EventType.CARD_SPAWN,
            EventType.CARD_SELECT,
            EventType.PROP_UPDATE,
        ]
    ).order_by(Event.server_time)

    # Integrate all prop, cardset and card spawn events up to the given event, to get the current card state
    cards = []
    cards_by_loc = {}
    for event in card_events:
        if event.type == EventType.CARD_SET:
            data = orjson.loads(event.data)
            set_cards = [Card.from_dict(card) for card in data["cards"]]
            # Clear cards that were in the set
            for card in set_cards:
                cards_by_loc[card.location] = None
        if event.type == EventType.CARD_SPAWN:
            data = orjson.loads(event.data)
            card = Card.from_dict(data)
            cards_by_loc[card.location] = card
        if event.type == EventType.CARD_SELECT:
            card = Card.from_json(event.data)
            cards_by_loc[card.location] = card
        elif event.type == EventType.PROP_UPDATE:
            # Regen props from the prop update
            prop_update = PropUpdate.from_json(event.data)
            cards = [
                Card.FromProp(prop)
                for prop in prop_update.props
                if prop.prop_type == PropType.CARD
            ]
            cards_by_loc = {}
            for card in cards:
                cards_by_loc[card.location] = card

    cards = cards_by_loc.values()
    # Filter out None values
    cards = [card for card in cards if card is not None]
    logger.debug(f"Detected {len(cards)} cards in the game. at this point.")

    turn_record_query = game_events.where(
        Event.type << [EventType.TURN_STATE, EventType.START_OF_TURN],
    ).order_by(Event.server_time.desc())
    turn_state = None
    if turn_record_query.count() == 0:
        # Initial turn.
        turn_state = TurnUpdate(
            Role.LEADER,
            LEADER_MOVES_PER_TURN,
            6,
            datetime.utcnow()
            + TurnDuration(Role.LEADER),  # pylint: disable=protected-access
            datetime.utcnow(),
            0,
            0,
            0,
        )
    else:
        turn_record = turn_record_query.first()
        turn_state = TurnState.from_json(turn_record.data)

    # Integrate all instruction events up to the given event, to get the current instruction state
    instruction_list = []
    instruction_events = game_events.where(
        Event.type
        << [
            EventType.INSTRUCTION_SENT,
            EventType.INSTRUCTION_ACTIVATED,
            EventType.INSTRUCTION_CANCELLED,
            EventType.INSTRUCTION_DONE,
        ]
    ).order_by(Event.server_time)
    instruction_list = []
    for event in instruction_events:
        if event.type == EventType.INSTRUCTION_SENT:
            instruction_list.append(objective.ObjectiveMessage.from_json(event.data))
        if event.type == EventType.INSTRUCTION_ACTIVATED:
            parent_instruction_event = event.parent_event
            instruction = objective.ObjectiveMessage.from_json(
                parent_instruction_event.data
            )
            if instruction_list[0].uuid != instruction.uuid:
                return (
                    None,
                    f"Activated instruction {instruction.uuid} not found in instruction list.",
                )
        if event.type == EventType.INSTRUCTION_CANCELLED:
            parent_instruction_event = event.parent_event
            instruction = objective.ObjectiveMessage.from_json(
                parent_instruction_event.data
            )
            try:
                if instruction_list[0].uuid != instruction.uuid:
                    return (
                        None,
                        f"Cancelled instruction {event.data} not found in instruction list.",
                    )
            except IndexError:
                # Print the list of instructions.
                logger.debug(
                    f"Instruction list is empty. ================ cancelled: {instruction.uuid}"
                )
                for instruction in instruction_list:
                    logger.debug(f"Instruction: {instruction.uuid}")
                # raise e
            if len(instruction_list) > 0:
                logger.debug(f"Cancelled: {instruction_list[0].uuid}")
                # Delete the instruction from the list.
                instruction_list = instruction_list[1:]
        if event.type == EventType.INSTRUCTION_DONE:
            parent_instruction_event = event.parent_event
            instruction = objective.ObjectiveMessage.from_json(
                parent_instruction_event.data
            )
            # Make sure this instruction is at the head of the list.
            if instruction_list[0].uuid != instruction.uuid:
                return (
                    None,
                    f"Done instruction {event.data} not found in instruction list.",
                )
            # Delete the instruction from the list.
            instruction_list = instruction_list[1:]

    initial_state_event = game_events.where(
        Event.type == EventType.INITIAL_STATE,
    )
    if initial_state_event.count() != 1:
        return (
            None,
            f"Single initial state event not found. ({initial_state_event.count()} found)",
        )
    initial_state_event = initial_state_event.get()
    initial_state = InitialState.from_json(initial_state_event.data)

    leader = Actor(
        21,
        0,
        Role.LEADER,
        initial_state.leader_position,
        False,
        initial_state.leader_rotation_degrees,
    )
    follower = Actor(
        22,
        0,
        Role.FOLLOWER,
        initial_state.follower_position,
        False,
        initial_state.follower_rotation_degrees,
    )

    moves = game_events.where(Event.type == EventType.ACTION)
    logger.debug(f"Found {moves.count()} moves before event {event_uuid}")
    for move in moves:
        action = action_module.Action.from_json(move.data)
        if action.action_type not in [
            action_module.ActionType.INIT,
            action_module.ActionType.INSTANT,
            action_module.ActionType.ROTATE,
            action_module.ActionType.TRANSLATE,
        ]:
            continue
        if move.origin == EventOrigin.LEADER:
            leader.add_action(action)
            leader.step()
        elif move.origin == EventOrigin.FOLLOWER:
            follower.add_action(action)
            follower.step()
        else:
            return None, f"Unknown event origin: {move.origin}"
    state_sync_msg = StateSync(2, [leader.state(), follower.state()], -1, Role.NONE)

    return (
        Scenario(
            "",
            map_update,
            PropUpdate(props=[card.prop() for card in cards]),
            turn_state,
            instruction_list,
            state_sync_msg,
        ),
        None,
    )


def GameStateFromScenario(scenario: Scenario) -> GameState:
    """Creates a GameState from a Scenario."""
    return GameState(
        scenario.map,
        scenario.prop_update.props,
        scenario.turn_state,
        scenario.objectives,
        [Actor.from_state(state) for state in scenario.actor_state.actors],
        live_feedback=scenario.live_feedback,
    )


def ScenarioFromGameState(state: GameState) -> Scenario:
    """Creates a scenario from a gamestate."""
    return Scenario(
        state.map_update,
        PropUpdate(props=state.props),
        state.turn_state,
        state.instructions,
        [actor.state() for actor in state.actors],
        state.live_feedback,
    )
