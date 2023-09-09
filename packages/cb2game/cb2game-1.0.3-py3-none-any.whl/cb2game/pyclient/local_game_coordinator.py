""" This file defines utilities for coordinating and matching local gym environments.

    Each local game has a unique game name, and agent environments use this name to
    find each other. The game coordinator is responsible for matching agents to

"""

import logging
import sys
import uuid
from collections import deque
from datetime import datetime, timedelta

import pygame

import cb2game.server.schemas.game as game_db
from cb2game.pyclient.game_endpoint import GameEndpoint
from cb2game.pyclient.game_socket import GameSocket
from cb2game.server.lobbies.open_lobby import OpenLobby
from cb2game.server.lobby import Lobby
from cb2game.server.lobby_consts import LobbyInfo, LobbyType
from cb2game.server.map_tools.visualize import GameDisplay
from cb2game.server.messages.rooms import Role
from cb2game.server.messages.tutorials import (
    FOLLOWER_TUTORIAL,
    LEADER_TUTORIAL,
    RoleFromTutorialName,
)
from cb2game.server.state import State
from cb2game.server.state_machine_driver import StateMachineDriver
from cb2game.server.tutorial_state import TutorialGameState
from cb2game.server.util import GetCommitHash, PackageVersion

logger = logging.getLogger(__name__)

DEFAULT_LOBBY = OpenLobby(
    LobbyInfo(LobbyType.OPEN, "default local game coordinator lobby")
)

# pylint: disable=protected-access
class LocalSocket(GameSocket):
    """Used to manage state machines for local games, each with two agents.

    Note that CreateGameFromDatabase() can be used instead of CreateGame() to
    create a game which is initialized from a specific instruction in a recorded
    game.

    """

    def __init__(self, local_coordinator, game_name: str, actor_id: int):
        self.local_coordinator = local_coordinator
        self.game_name = game_name
        self.actor_id = actor_id
        # A list of received messages, in order from oldest to newest. Use like FIFO.
        self.received_messages = deque()

    def send_message(self, message):
        state_machine_driver = self.local_coordinator._state_machine_driver(
            self.game_name
        )
        state_machine_driver.drain_messages(self.actor_id, [message])
        self.local_coordinator.StepGame(self.game_name)

    def connected(self):
        return self.local_coordinator._game_exists(self.game_name)

    def receive_message_nowait(self):
        ...

    def receive_message(self, timeout=timedelta(seconds=60)):
        """This is a local socket. We don't need to worry about timeouts. No blocking operations."""
        # Give the state machine a chance to run.
        end_time = datetime.utcnow() + timeout
        ran_once = False
        # Wait until we have at least one message to return. Run at least once.
        while datetime.utcnow() < end_time or not ran_once:
            self.local_coordinator.StepGame(self.game_name)
            state_machine_driver = self.local_coordinator._state_machine_driver(
                self.game_name
            )
            state_machine_driver.fill_messages(self.actor_id, self.received_messages)
            if len(self.received_messages) > 0:
                return self.received_messages.popleft(), ""
            ran_once = True
        return None, "No messages available."


# pylint: enable=protected-access


class LocalGameCoordinator:
    """Used for starting local games.

    Can run multiple simulated games at once, each with two agents.
    Can start games from a specific instruction in a recorded game.

    """

    def __init__(
        self, config, render_leader: bool = False, render_follower: bool = False
    ):
        self._game_drivers = {}  # Game name -> StateMachineDriver
        self._game_endpoints = {}  # Game name -> (leader_endpoint, follower_endpoint)
        self._render_leader = render_leader
        self._render_follower = render_follower
        self._config = config

    def CreateGame(
        self,
        log_to_db: bool = True,
        realtime_actions: bool = False,
        lobby: Lobby = DEFAULT_LOBBY,
    ):
        """Creates a new game. Exactly two agents can join this game with JoinGame().

        Returns the game name.
        """
        if realtime_actions and "unittest" not in sys.modules:
            logger.warning(
                " ".join(
                    [
                        "Warning, realtime actions are intended for unit tests.",
                        "Enabling them in self-play will cause the game to run very",
                        "slowly as the state machine waits for each animation to",
                        "complete.",
                    ]
                )
            )
        game_name = self._unique_game_name()
        if game_name in self._game_drivers:
            raise Exception(
                f"Game name {game_name} already exists. This should never happen."
            )
        room_id = game_name
        # Setup game DB entry.
        if log_to_db:
            game_record = game_db.Game()
            game_id = game_record.id
            game_time = datetime.now().strftime("%Y-%m-%dT%Hh.%Mm.%Ss%z")
            game_name = f"{game_time}_{game_id}_GAME"
            game_record.server_software_commit = GetCommitHash() or PackageVersion()
            game_record.type = "local-simulated|0|simulated"
            game_record.save()
        else:
            game_record = None
        state_machine = State(
            room_id,
            game_record,
            log_to_db=log_to_db,
            realtime_actions=False,
            lobby=lobby,
        )
        self._game_drivers[game_name] = StateMachineDriver(state_machine, room_id)
        return game_name

    def CreateGameFromDatabase(
        self, event_uuid: str, log_to_db: bool = False, lobby: Lobby = DEFAULT_LOBBY
    ):
        """Creates a new game from a specific instruction in a recorded game.

        Exactly two agents can join this game with JoinGame().
        Returns the game name.
        """
        game_name = self._unique_game_name()
        if game_name in self._game_drivers:
            raise Exception(
                f"Game name {game_name} already exists. This should never happen."
            )
        room_id = game_name

        # For cards, take all cards so far and then delete any CardSets().
        state_machine, reason = State.InitializeFromExistingState(
            room_id,
            event_uuid,
            realtime_actions=False,
            log_to_db=log_to_db,
            lobby=lobby,
        )
        assert (
            state_machine is not None
        ), f"Failed to init from event {event_uuid}: {reason}"
        state_machine.state(-1)

        self._game_drivers[game_name] = StateMachineDriver(state_machine, room_id)
        return game_name

    def CreateLeaderTutorial(self, realtime: bool = True):
        """Creates a new game. Exactly two agents can join this game with JoinGame().

        Returns the game name.
        """
        return self._CreateTutorial(LEADER_TUTORIAL, realtime)

    def CreateFollowerTutorial(self, realtime: bool = True):
        """Creates a new game. Exactly two agents can join this game with JoinGame().

        Returns the game name.
        """
        return self._CreateTutorial(FOLLOWER_TUTORIAL, realtime)

    def _CreateTutorial(
        self, tutorial_name: str, realtime: bool, lobby: Lobby = DEFAULT_LOBBY
    ):
        """Creates a tutorial game. One-player only.

        Returns the game name.
        """
        game_name = self._unique_game_name()
        if game_name in self._game_drivers:
            raise Exception(
                f"Game name {game_name} already exists. This should never happen."
            )
        room_id = game_name
        role = RoleFromTutorialName(tutorial_name)
        opposite_role = Role.FOLLOWER if role == Role.LEADER else Role.LEADER
        # Setup game DB entry.
        game_record = game_db.Game()
        game_id = game_record.id
        game_time = datetime.now().strftime("%Y-%m-%dT%Hh.%Mm.%Ss%z")
        game_name = f"{game_time}_{game_id}_GAME"
        game_record.server_software_commit = GetCommitHash() or PackageVersion()
        game_record.type = "local-simulated|0|tutorial"
        game_record.save()
        # The value
        state_machine = TutorialGameState(
            room_id, tutorial_name, game_record, realtime, lobby=lobby
        )
        self._game_endpoints[game_name] = (None, None)
        self._game_drivers[game_name] = StateMachineDriver(state_machine, room_id)
        return game_name

    def DrawGame(self, game_name):
        """Draws the game state to the screen using pygame."""
        if game_name not in self._game_drivers:
            raise Exception(f"Game {game_name} does not exist.")
        display = GameDisplay(800)
        display.set_config(self._config)
        state_machine = self._game_drivers[game_name].state_machine()
        state_sync = state_machine.state(-1)
        # pylint: disable=protected-access
        display.set_instructions(state_machine._objectives)
        # pylint: enable=protected-access
        display.set_map(state_machine.map())
        cards = state_machine.cards()
        display.set_props([card.prop() for card in cards])
        display.set_state_sync(state_sync)
        display.draw()
        pygame.display.flip()

    def JoinTutorial(self, game_name, role: Role):
        """Joins a tutorial with the given name.

        Returns a Game object used to interact with the game.
        """
        return self.JoinSinglePlayerGame(game_name, role)

    def JoinSinglePlayerGame(self, game_name, role: Role):
        """Joins a single player game with the given name.

        If the game doesn't exist, crashes.

        Returns a Game object used to interact with the game.
        """
        # If the game doesn't exist, crash.
        if game_name not in self._game_drivers:
            raise ValueError(
                f"Game {game_name} doesn't exist. Create it first with CreateGame()."
            )

        game_driver = self._game_drivers[game_name]
        state_machine = game_driver.state_machine()

        actor_id = state_machine.create_actor(role)
        render = self._render_leader if role == Role.LEADER else self._render_follower
        game_endpoint = GameEndpoint(
            LocalSocket(self, game_name, actor_id), self._config, render
        )

        # Register endpoints for this game so we can initialize them in StartGame().
        if role == Role.LEADER:
            self._game_endpoints[game_name] = (game_endpoint, None)
        else:
            self._game_endpoints[game_name] = (None, game_endpoint)
        return game_endpoint

    def JoinGame(self, game_name):
        """Joins a game with the given name.

        If the game doesn't exist, crashes.
        If the game already has two players, crashes.

        Returns a Game object used to interact with the game.
        """
        # If the game doesn't exist, crash.
        if game_name not in self._game_drivers:
            raise ValueError(
                f"Game {game_name} doesn't exist. Create it first with CreateGame()."
            )

        # If the game exists, choose role depending on number of players.
        game_driver = self._game_drivers[game_name]
        state_machine = game_driver.state_machine()

        number_players = len(state_machine.player_ids())

        if number_players >= 2:
            raise Exception(
                f"Game is full! Number of players: {len(state_machine.player_ids())}"
            )

        # If the game has one player, join as leader. Else, follow.
        role = Role.LEADER if number_players == 0 else Role.FOLLOWER
        actor_id = state_machine.create_actor(role)
        assert actor_id is not None, "Actor ID should not be None."
        render = self._render_leader if role == Role.LEADER else self._render_follower
        game_endpoint = GameEndpoint(
            LocalSocket(self, game_name, actor_id), self._config, render
        )
        # Register endpoints for this game so we can initialize them in StartGame().
        if number_players == 0:
            self._game_endpoints[game_name] = (game_endpoint, None)
        else:
            leader = self._game_endpoints[game_name][0]
            self._game_endpoints[game_name] = (leader, game_endpoint)
        return game_endpoint

    def StepGame(self, game_name):
        """Runs one iteration of the game state machine."""
        game_driver = self._state_machine_driver(game_name)
        game_driver.step()

    def TickCount(self, game_name):
        """Returns the number of ticks that have passed in the game."""
        return self._state_machine_driver(game_name).state_machine().tick_count()

    def Cleanup(self):
        """Cleans up any games that have ended. Call this regularly to avoid memory leaks."""
        # list() call is necessary to create a copy. Otherwise we're mutating a
        # list as we iterate through it.
        for game_name in list(self._game_drivers.keys()):
            game_driver = self._game_drivers[game_name]
            if game_driver.state_machine().done():
                logger.info(f"Game {game_name} has ended. Cleaning up.")
                game_driver.state_machine().on_game_over()
                del self._game_drivers[game_name]
                del self._game_endpoints[game_name]

    def ForceCleanAll(self):
        """Cleans up any games that are running or have ended."""
        for game_name in list(self._game_drivers.keys()):
            logger.info(f"Forcefully cleaning game {game_name} driver.")
            del self._game_drivers[game_name]
        for game_name in list(self._game_endpoints.keys()):
            logger.info(f"Forcefully cleaning game {game_name} endpoint.")
            del self._game_endpoints[game_name]

    @staticmethod
    def _unique_game_name():
        """Generates a random UUID and returns.

        UUIDs are 128 bits, you only have to worry about odds of a duplicate
        once you reach ~quintillions of UUIDs generated. Note that I'm not sure
        if this is threadsafe, but some brief research online has me convinced
        this should work.

        Mathematical analysis of collision chances:
        https://en.wikipedia.org/wiki/Universally_unique_identifier#Collisions
        """
        return str(uuid.uuid4())

    def _state_machine_driver(self, game_name: str):
        if game_name not in self._game_drivers:
            raise ValueError(f"Game {game_name} doesn't exist.")
        return self._game_drivers[game_name]

    def _game_exists(self, game_name: str):
        return game_name in self._game_drivers
