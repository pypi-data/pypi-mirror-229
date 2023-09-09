import asyncio
import logging
import pathlib
import queue
import tempfile
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from queue import Queue
from typing import List, Tuple

import orjson
from aiohttp import web
from dataclasses_json import dataclass_json

import cb2game.server.messages.message_from_server as message_from_server
import cb2game.server.messages.message_to_server as message_to_server
import cb2game.server.schemas.game as game_db
from cb2game.server.config.config import GlobalConfig, LobbyInfo
from cb2game.server.lobby_consts import LobbyInfo, LobbyType
from cb2game.server.map_provider import CachedMapRetrieval
from cb2game.server.messages.logs import GameInfo
from cb2game.server.messages.menu_options import (
    ButtonCode,
    ButtonDescriptor,
    MenuOptions,
)
from cb2game.server.messages.replay_messages import ReplayRequest
from cb2game.server.messages.rooms import (
    JoinResponse,
    LeaveRoomNotice,
    Role,
    RoomManagementRequest,
    RoomManagementResponse,
    RoomRequestType,
    RoomResponseType,
    StatsResponse,
)
from cb2game.server.messages.scenario import (
    ScenarioRequestType,
    ScenarioResponse,
    ScenarioResponseType,
)
from cb2game.server.messages.tutorials import (
    RoleFromTutorialName,
    TutorialRequestType,
    TutorialResponse,
    TutorialResponseType,
)
from cb2game.server.room import Room, RoomType
from cb2game.server.util import (
    GetCommitHash,
    IdAssigner,
    LatencyMonitor,
    PackageVersion,
)

logger = logging.getLogger(__name__)


@dataclass_json()
@dataclass(frozen=True)
class SocketInfo:
    room_id: int
    player_id: int
    role: Role

    def as_tuple(self):
        """This is a bit of a hack, since it's sensitive to changes in the SocketInfo class.

        Reasons for doing this:
        - SocketInfo is relatively unchanged and small over a long period of time.
        - Dataclasses's astuple method is extremely inefficient (over half of stream_game_state execution time). This will save us 26us.
        - I have higher priority things to be doing than finding the best way to do this. It's not within the scope of this paper.
        """
        return (self.room_id, self.player_id, self.role)


""" This interface abstracts over different types of game lobbies.

    Lobbies manage a collection of games. They are responsible for creating new
    games, handling players joining and leaving games, matchmaking, and managing
    the game objects.

    Each lobby has 3 queues: Leader-only, Follower-only, and "either" (player
    queue). Additionally, each player may have a qualification or experience the
    lobby uses to determine their role in the game. For example, the mturk lobby
    (mturk_lobby.py) checks player experience from the database to determine
    which player is more experienced in the leader role.

    Lobbies exist to separate players by category. For example, a lobby might
    exist only for mturk workers or only for users who have been authenticated
    with Google SSO.

    The parent Lobby object has a matchmaking process and a room cleanup
    process. These must be launched with something like:

    ```
        tasks = asyncio.gather(lobby.matchmake(), lobby.cleanup_rooms(), ...)
        loop.run_until_complete(tasks)
    ```

    Or alternatively, depending on your usecase, `loop.create_task()` can be used.
"""


class Lobby(ABC):
    @abstractmethod
    def __init__(self, lobby_info: LobbyInfo):
        """This class is abstract. Must call super().__init__() in subclasses."""
        self._lobby_name = lobby_info.name
        self._lobby_comment = lobby_info.comment
        self._game_capacity = lobby_info.game_capacity
        self._lobby_info = lobby_info
        self._rooms = {}
        self._room_id_assigner = IdAssigner()
        self._remotes = {}  # {ws: SocketInfo}
        self._is_done = False
        # Queues of (queue_join_time, websocket, RoomManagementRequest). Players waiting to join a game.
        self._player_queue = deque()
        self._follower_queue = deque()
        self._leader_queue = deque()
        self._base_log_directory = pathlib.Path("/dev/null")
        self._pending_room_management_responses = {}  # {ws: room_management_response}
        self._pending_tutorial_messages = {}  # {ws: tutorial_response}
        self._pending_replay_messages = {}  # {ws: replay_response}
        self._pending_scenario_messages = {}  # {ws: scenario_response}
        self._matchmaking_exc = None
        self._latency_monitor = LatencyMonitor()

    @abstractmethod
    def get_leader_follower_match(
        self,
    ) -> Tuple[web.WebSocketResponse, web.WebSocketResponse, str]:
        """Returns a leader-follower match, or None if no match is available.

        Returns a tuple of (leader, follower, event_uuid="").

        This function is also responsible for removing these entries from the queues.

        Third return value is the event uuid to start the game from, if
        applicable. This is determined from UUIDs the clients may have
        requested.
        """
        ...

    @abstractmethod
    def handle_join_request(
        self, request: RoomManagementRequest, ws: web.WebSocketResponse
    ) -> None:
        """Handles a join request from a player.

        You should use the following functions to put the player in a queue:
        self.join_player_queue(ws, request)
        self.join_follower_queue(ws, request)
        self.join_leader_queue(ws, request)

        If the player isn't valid, reject them by calling:
        self.boot_from_queue(ws)
        """
        ...

    @abstractmethod
    def handle_replay_request(
        self, request: ReplayRequest, ws: web.WebSocketResponse
    ) -> None:
        """Handles a replay request from a player."""
        ...

    @abstractmethod
    def lobby_type(self) -> "LobbyType":  # Lazy type annotations.
        """Returns the lobby type."""
        ...

    def menu_options(self, ws: web.WebSocketResponse):
        return MenuOptions(
            [
                ButtonDescriptor(
                    ButtonCode.JOIN_QUEUE,
                    "Join Game",
                    "Joins the queue for this lobby",
                ),
            ],
            "",
        )

    def lobby_name(self):
        return self._lobby_name

    def lobby_comment(self):
        return self._lobby_comment

    def latency_monitor(self):
        return self._latency_monitor

    def register_game_logging_directory(self, dir) -> None:
        """Each lobby has its own log directory. Game logs are written to this directory."""
        self._base_log_directory = dir

    def player_queue(self) -> List[Tuple[(datetime, web.WebSocketResponse, str)]]:
        """Query the player queue.

        Returns a list of tuples of (queue_entry_time, websocket, event_uuid).
        """
        return self._player_queue

    def leader_queue(self) -> List[Tuple[(datetime, web.WebSocketResponse, str)]]:
        """Query the leader queue.

        Returns a list of tuples of (queue_entry_time, websocket, event_uuid).
        """
        return self._leader_queue

    def follower_queue(self) -> List[Tuple[(datetime, web.WebSocketResponse, str)]]:
        """Query the follower queue.

        Returns a list of tuples of (queue_entry_time, websocket, event_uuid).
        """
        return self._follower_queue

    def disconnect_socket(self, ws):
        """This socket terminated its connection. End the game that the person was in."""
        logger.info(f"disconnect_socket()")
        self.remove_socket_from_queue(ws)
        if not ws in self._remotes:
            logging.info("Socket not found in self._remotes!")
            return
        room_id, player_id, _ = self._remotes[ws].as_tuple()
        del self._remotes[ws]
        if not room_id in self._rooms:
            # The room was already terminated by the other player.
            return
        removed_role = self._rooms[room_id].player_role(player_id)
        logger.info(f"disconnect_socket() removed role: {removed_role}")
        self._rooms[room_id].remove_player(player_id, ws, disconnected=True)
        # If a player leaves, the game ends for everyone in the room. Send them
        # leave notices and end the game. Unless it's a spectator. In
        # that case, just remove them.
        if (removed_role == Role.SPECTATOR) and not self._rooms[room_id].is_empty():
            return
        for socket in self._rooms[room_id].player_endpoints():
            if not socket.closed:
                leave_notice = LeaveRoomNotice(
                    "Other player disconnected, game ending."
                )
                self._pending_room_management_responses[socket].put(
                    RoomManagementResponse(
                        RoomResponseType.LEAVE_NOTICE, None, None, leave_notice
                    )
                )
                del self._remotes[socket]
        self._rooms[room_id].stop()
        del self._rooms[room_id]

    async def matchmake(self):
        """Runs asynchronously, creating rooms for pending followers and
        leaders."""
        while not self._is_done:
            try:
                await asyncio.sleep(0.5)
                # If the first follower has been waiting for 5m, remove them from the queue.
                if len(self._follower_queue) > 0:
                    (ts, follower, e_uuid) = self._follower_queue[0]
                    if datetime.now() - ts > timedelta(minutes=5):
                        self._follower_queue.popleft()
                        # Queue a room management response to notify the follower that they've been removed from the queue.
                        self.boot_from_queue(
                            follower,
                            "You've been removed from the queue for waiting too long.",
                        )

                # If a general player has been waiting alone for 5m, remove them from the queue.
                if len(self._player_queue) > 0:
                    (ts, player, e_uuid) = self._player_queue[0]
                    if datetime.now() - ts > timedelta(minutes=5):
                        self._player_queue.popleft()
                        # Queue a room management response to notify the player that they've been removed from the queue.
                        self.boot_from_queue(
                            player,
                            "You've been removed from the queue for waiting too long.",
                        )

                # If a leader has been waiting alone for 5m, remove them from the queue.
                if len(self._leader_queue) > 0:
                    (ts, leader, e_uuid) = self._leader_queue[0]
                    if datetime.now() - ts > timedelta(minutes=5):
                        self._leader_queue.popleft()
                        # Queue a room management response to notify the leader that they've been removed from the queue.
                        self.boot_from_queue(
                            leader,
                            "You've been removed from the queue for waiting too long.",
                        )

                # If the lobby is full, return early.
                if len(self._rooms) >= self._game_capacity:
                    logger.info(
                        f"Lobby {self._lobby_name} is full. Refusing to matchmake until rooms are cleaned up."
                    )
                    continue

                leader, follower, event_uuid = self.get_leader_follower_match()

                if (leader is None) and (follower is None):
                    continue

                # Scenario games.
                if (follower is not None) and (leader is None):
                    # Follower-only games are allowed for scenario lobbies.
                    if self.lobby_type() == LobbyType.SCENARIO:
                        logger.info(
                            f"Creating room for {follower}. Queue size: {len(self._player_queue)} Follower Queue: {len(self._follower_queue)}"
                        )

                        game_record = game_db.Game()
                        game_record.save()
                        game_id = game_record.id
                        game_record.log_directory = ""
                        game_record.server_software_commit = (
                            GetCommitHash() or PackageVersion()
                        )
                        game_record.save()

                        room = self.create_room(game_id, game_record, RoomType.SCENARIO)

                        if (room is None) or (not room.initialized()):
                            logger.warning(f"Error creating room.")
                            # Boot the follower from the queue.
                            self.boot_from_queue(follower, "Error creating room.")

                        follower_id = room.add_player(follower, Role.FOLLOWER)
                        self._remotes[follower] = SocketInfo(
                            room.id(), follower_id, Role.FOLLOWER
                        )
                        # Tell the follower they've joined a room!
                        self._pending_room_management_responses[follower].put(
                            RoomManagementResponse(
                                RoomResponseType.JOIN_RESPONSE,
                                None,
                                JoinResponse(
                                    True, 0, Role.FOLLOWER, False, "", game_id
                                ),
                                None,
                                None,
                            )
                        )
                        continue
                    else:
                        # If the lobby type is not scenario, then we don't want to create a follower-only game.
                        # Send the follower a join response indicating that they were not added to a room.
                        continue

                if (leader is None) or (follower is None):
                    continue

                logger.info(
                    f"Creating room for {leader} and {follower}. Queue size: {len(self._player_queue)} Follower Queue: {len(self._follower_queue)}"
                )

                if event_uuid is not None and event_uuid != "":
                    logger.info(f"Starting game from event: {event_uuid}")
                    # Start game from a specific point.
                    room = self.create_room(
                        event_uuid, None, RoomType.PRESET_GAME, "", event_uuid
                    )

                    if (room is None) or (not room.initialized()):
                        logger.warning(f"Error creating room from UUID {event_uuid}")
                        # Boot the leader & follower from the queue.
                        self.boot_from_queue(leader, "Error creating room.")
                        self.boot_from_queue(follower, "Error creating room.")
                        continue

                    logger.info(f"Creating new game from event {room.name()}")
                    leader_id = room.add_player(leader, Role.LEADER)
                    follower_id = room.add_player(follower, Role.FOLLOWER)
                    self._remotes[leader] = SocketInfo(
                        room.id(), leader_id, Role.LEADER
                    )
                    self._remotes[follower] = SocketInfo(
                        room.id(), follower_id, Role.FOLLOWER
                    )
                    logger.info(f"JOINING ROOM {room.id()} {leader_id} {follower_id}")
                    self._pending_room_management_responses[leader].put(
                        RoomManagementResponse(
                            RoomResponseType.JOIN_RESPONSE,
                            None,
                            JoinResponse(True, 0, Role.LEADER, False, "", room.id()),
                            None,
                            None,
                        )
                    )
                    self._pending_room_management_responses[follower].put(
                        RoomManagementResponse(
                            RoomResponseType.JOIN_RESPONSE,
                            None,
                            JoinResponse(True, 0, Role.FOLLOWER, False, "", room.id()),
                            None,
                            None,
                        )
                    )
                    continue

                # Setup room log directory.
                game_record = game_db.Game()
                game_record.save()
                game_id = game_record.id
                game_time = datetime.now().strftime("%Y-%m-%dT%Hh.%Mm.%Ss%z")
                game_name = f"{game_time}_{game_id}_GAME"
                log_directory = pathlib.Path(self._base_log_directory, game_name)
                log_directory.mkdir(parents=False, exist_ok=False)
                game_record.log_directory = str(log_directory)
                game_record.server_software_commit = GetCommitHash() or PackageVersion()
                game_record.save()

                # Create room.
                room = self.create_room(game_id, game_record)
                if room is None or not room.initialized():
                    logger.warning(f"Error creating room")
                    # Boot the leader & follower from the queue.
                    self.boot_from_queue(leader, "Error creating room.")
                    self.boot_from_queue(follower, "Error creating room.")
                    continue
                print("Creating new game " + room.name())
                leader_id = room.add_player(leader, Role.LEADER)
                follower_id = room.add_player(follower, Role.FOLLOWER)
                self._remotes[leader] = SocketInfo(room.id(), leader_id, Role.LEADER)
                self._remotes[follower] = SocketInfo(
                    room.id(), follower_id, Role.FOLLOWER
                )

                game_info_path = pathlib.Path(log_directory, "game_info.jsonl.log")
                game_info_log = game_info_path.open("w")
                game_info = GameInfo(
                    datetime.now(),
                    game_id,
                    game_name,
                    [Role.LEADER, Role.FOLLOWER],
                    [leader_id, follower_id],
                )
                json_str = orjson.dumps(
                    game_info,
                    option=orjson.OPT_PASSTHROUGH_DATETIME,
                    default=datetime.isoformat,
                ).decode("utf-8")
                game_info_log.write(json_str + "\n")
                game_info_log.close()

                self._pending_room_management_responses[leader].put(
                    RoomManagementResponse(
                        RoomResponseType.JOIN_RESPONSE,
                        None,
                        JoinResponse(True, 0, Role.LEADER, False, "", game_id),
                        None,
                        None,
                    )
                )
                self._pending_room_management_responses[follower].put(
                    RoomManagementResponse(
                        RoomResponseType.JOIN_RESPONSE,
                        None,
                        JoinResponse(True, 0, Role.FOLLOWER, False, "", game_id),
                        None,
                        None,
                    )
                )
            except Exception as e:
                logger.exception(e)
                self._matchmaking_exc = e

    def socket_in_room(self, ws):
        return ws in self._remotes

    def socket_info(self, ws):
        return self._remotes[ws] if ws in self._remotes else None

    def get_room(self, id):
        return self._rooms[id] if id in self._rooms else None

    def get_room_by_name(self, name):
        for room in self._rooms.values():
            if room.name == name:
                return room

    def room_ids(self):
        return self._rooms.keys()

    def end_server(self):
        for room in self._rooms.values():
            room.stop()
        self._is_done = True

    def create_room(
        self,
        id,
        game_record: game_db.Game,
        type: RoomType = RoomType.GAME,
        tutorial_name: str = "",
        from_event: str = "",
    ):
        """
        Creates a new room & starts an asyncio task to run the room's state machine.

        Returns the room, or None if startup failed.
        """
        room = Room(
            # Room name.
            "Room #" + str(id) + ("(TUTORIAL)" if type == RoomType.TUTORIAL else ""),
            # Max number of players.
            2,
            # Room ID.
            id,
            game_record,
            self,
            type,
            tutorial_name,
            from_event,
        )
        if not room.initialized():
            return None
        self._rooms[id] = room
        self._rooms[id].start()
        return self._rooms[id]

    def lobby_info(self) -> LobbyInfo:
        return self._lobby_info

    def delete_unused_rooms(self):
        rooms = list(self._rooms.values())
        for room in rooms:
            if room.done() and not room.has_pending_messages():
                logger.info(f"Deleting unused room: {room.name()}")
                self.delete_room(room.id())
            if room.has_exception():
                logger.info(f"Room {room.name()} has an exception. Terminating game!")
                # Grab the global config.
                config = GlobalConfig()
                exception_directory = config.exception_directory()

                # If the exception directory exists, create a temporary file with the exception type, date, and time.
                if exception_directory is not None:
                    exception_file = tempfile.NamedTemporaryFile(
                        mode="w",
                        prefix=(
                            str(room.id())
                            + "_gameid_"
                            + type(room.exception()).__name__
                            + "_"
                        ),
                        suffix=".txt",
                        dir=exception_directory,
                        delete=False,
                    )
                    exception_file.write(str(room.traceback()))
                    exception_file.close()

                # Close the room.
                for socket in room.player_endpoints():
                    if not socket.closed:
                        leave_notice = LeaveRoomNotice(
                            f"Game ended by server due to: {type(room.exception()).__name__}"
                        )
                        self._pending_room_management_responses[socket].put(
                            RoomManagementResponse(
                                RoomResponseType.LEAVE_NOTICE, None, None, leave_notice
                            )
                        )
                self.delete_room(room.id())
            if room.game_time() > timedelta(hours=3):
                logger.info(
                    f"Room {room.name()} expired after 3 hours. Terminating game!"
                )
                for socket in room.player_endpoints():
                    if not socket.closed:
                        leave_notice = LeaveRoomNotice(
                            "Game ended by server after 3 hours."
                        )
                        self._pending_room_management_responses[socket].put(
                            RoomManagementResponse(
                                RoomResponseType.LEAVE_NOTICE, None, None, leave_notice
                            )
                        )
                self.delete_room(room.id())

    def delete_room(self, id):
        if id not in self._rooms:
            logger.warning(f"Room {id} does not exist. Cannot delete.")
            return
        self._rooms[id].stop()
        player_endpoints = list(self._rooms[id].player_endpoints())
        for ws in player_endpoints:
            if ws not in self._remotes:
                logger.warning(
                    f"Player {ws} not found in remotes. Cannot remove from room."
                )
                continue
            room_id, player_id, _ = self._remotes[ws].as_tuple()
            self._rooms[id].remove_player(player_id, ws, disconnected=False)
            del self._remotes[ws]
        del self._rooms[id]

    def available_room_id(self):
        for room_id in self._rooms.keys():
            if not self._rooms[room_id].is_full():
                return room_id
        return None

    async def cleanup_rooms(self):
        while not self._is_done:
            await asyncio.sleep(5)
            self.delete_unused_rooms()

    def create_tutorial(self, player: web.WebSocketResponse, tutorial_name):
        logger.info(f"Creating tutorial room for {player}.")

        # Setup room log directory.
        game_record = game_db.Game()
        game_record.save()
        game_id = game_record.id
        game_time = datetime.now().strftime("%Y-%m-%dT%Hh.%Mm.%Ss%z")
        game_name = f"{game_time}_{game_id}_TUTORIAL"
        log_directory = pathlib.Path(self._base_log_directory, game_name)
        log_directory.mkdir(parents=False, exist_ok=False)
        game_record.log_directory = str(log_directory)
        game_record.server_software_commit = GetCommitHash() or PackageVersion()
        game_record.save()

        # Create room.
        room = self.create_room(game_id, game_record, RoomType.TUTORIAL, tutorial_name)
        if room is None:
            return None
        print("Creating new tutorial room " + room.name())
        role = RoleFromTutorialName(tutorial_name)
        player_id = room.add_player(player, role)
        self._remotes[player] = SocketInfo(room.id(), player_id, role)

        game_info_path = pathlib.Path(log_directory, "game_info.jsonl.log")
        game_info_log = game_info_path.open("w")
        game_info = GameInfo(datetime.now(), game_id, game_name, [role], [player_id])
        json_str = orjson.dumps(
            game_info,
            option=orjson.OPT_PASSTHROUGH_DATETIME,
            default=datetime.isoformat,
        ).decode("utf-8")
        game_info_log.write(json_str + "\n")
        game_info_log.close()
        return room

    def create_replay(self, player: web.WebSocketResponse, game_id):
        """Creates a replay room to view a replay of the provided game ID."""
        logger.info(f"Creating replay room for {player}.")

        # Setup room log directory.
        game_db.Game.select()
        game_record = game_db.Game.select().where(game_db.Game.id == game_id).get()

        # Create room.
        room = self.create_room(game_id, game_record, RoomType.REPLAY)
        if room is None:
            return None
        print("Creating new replay room " + room.name())
        player_id = room.add_player(player, Role.LEADER)
        self._remotes[player] = SocketInfo(room.id(), player_id, Role.LEADER)
        return room

    def create_demo(self, player: web.WebSocketResponse):
        """Creates a replay room to view a replay of the provided game ID."""
        logger.info(f"Creating replay room for {player}.")

        # Setup room log directory.
        game_id = 1
        game_record = None
        room = self.create_room(game_id, game_record, RoomType.DEMO)
        if room is None:
            return None
        print("Creating new DEMO room " + room.name())
        player_id = room.add_player(player, Role.LEADER)
        self._remotes[player] = SocketInfo(room.id(), player_id, Role.LEADER)
        return room

    def handle_tutorial_request(self, tutorial_request, ws):
        if ws not in self._pending_tutorial_messages:
            self._pending_tutorial_messages[ws] = Queue()
        if tutorial_request.type == TutorialRequestType.START_TUTORIAL:
            self.create_tutorial(ws, tutorial_request.tutorial_name)
            self._pending_tutorial_messages[ws].put(
                TutorialResponse(
                    TutorialResponseType.STARTED,
                    tutorial_request.tutorial_name,
                    None,
                    None,
                )
            )
        else:
            logger.warning(
                f"Room manager received incorrect tutorial request type {tutorial_request.type}."
            )

    def handle_scenario_request(self, scenario_request, ws):
        # If this isn't a scenario lobby, ignore.
        if self.lobby_type() != LobbyType.SCENARIO:
            logger.info("Scenario request received from non-scenario lobby. Ignoring.")
            return

        if ws not in self._pending_scenario_messages:
            self._pending_scenario_messages[ws] = Queue()

        if scenario_request.type == ScenarioRequestType.ATTACH_TO_SCENARIO:
            room_id = None
            for id, room in self._rooms.items():
                logger.info(f"room {id} has scenario {room.scenario_id()}")
                if room.scenario_id() == scenario_request.scenario_id:
                    room_id = id
                    break
            if room_id is None:
                logger.info(
                    f"Scenario {scenario_request.scenario_id} does not exist. Cannot attach."
                )
                self.boot_from_queue(ws, "Scenario does not exist. Could not attach.")
                return
            room = self._rooms[room_id]
            player_id = room.add_player(ws, Role.SPECTATOR)
            self._remotes[ws] = SocketInfo(room_id, player_id, Role.SPECTATOR)
            self._pending_scenario_messages[ws].put(
                ScenarioResponse(
                    ScenarioResponseType.LOADED,
                    None,
                )
            )
            self._pending_room_management_responses[ws].put(
                RoomManagementResponse(
                    RoomResponseType.JOIN_RESPONSE,
                    None,
                    JoinResponse(True, -1, Role.SPECTATOR, False, "", room.id()),
                    None,
                    None,
                )
            )

    def join_player_queue(self, ws, request: RoomManagementRequest):
        if ws in self._player_queue:
            logger.info(
                f"Join request is from socket which is already in the wait queue. Ignoring."
            )
            return
        if ws in self._follower_queue:
            logger.info(
                f"Join request is from socket which is already in the follow wait queue. Ignoring."
            )
            return
        if ws in self._leader_queue:
            logger.info(
                f"Join request is from socket which is already in the leader wait queue. Ignoring."
            )
            return
        self._player_queue.append(
            (datetime.now(), ws, request.join_game_with_event_uuid)
        )
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(
                RoomResponseType.JOIN_RESPONSE,
                None,
                JoinResponse(False, len(self._player_queue), Role.NONE),
                None,
                None,
            )
        )

    def join_follower_queue(self, ws, request: RoomManagementRequest):
        if ws in self._follower_queue:
            logger.info(
                f"Join request is from socket which is already in the follower wait queue. Ignoring."
            )
            return
        if ws in self._player_queue:
            logger.info(
                f"Join request is from follower socket which is already in the wait queue. Ignoring."
            )
            return
        if ws in self._leader_queue:
            logger.info(
                f"Join request is from socket which is already in the leader wait queue. Ignoring."
            )
            return
        self._follower_queue.append(
            (datetime.now(), ws, request.join_game_with_event_uuid)
        )
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(
                RoomResponseType.JOIN_RESPONSE,
                None,
                JoinResponse(False, len(self._follower_queue), Role.NONE),
                None,
                None,
            )
        )

    def join_leader_queue(self, ws, request: RoomManagementRequest = None):
        if ws in self._leader_queue:
            logger.info(
                f"Join request is from socket which is already in the leader wait queue. Ignoring."
            )
            return
        if ws in self._player_queue:
            logger.info(
                f"Join request is from leader socket which is already in the wait queue. Ignoring."
            )
            return
        if ws in self._follower_queue:
            logger.info(
                f"Join request is from leader socket which is already in the follow wait queue. Ignoring."
            )
            return
        self._leader_queue.append(
            (datetime.now(), ws, request.join_game_with_event_uuid)
        )
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(
                RoomResponseType.JOIN_RESPONSE,
                None,
                JoinResponse(False, len(self._leader_queue), Role.NONE),
                None,
                None,
            )
        )

    def boot_from_queue(self, ws, reason=""):
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(
                RoomResponseType.JOIN_RESPONSE,
                None,
                JoinResponse(False, -1, Role.NONE, True, reason),
                None,
                None,
            )
        )

    def handle_follower_only_join_request(self, request, ws):
        logger.info(
            f"Received follower only join request from : {str(ws)}. Queue size: {len(self._follower_queue)}. uuid: {request.join_game_with_event_uuid}"
        )
        self.join_follower_queue(ws, request)

    def handle_leader_only_join_request(self, request, ws):
        logger.info(
            f"Received leader only join request from : {str(ws)}. Queue size: {len(self._leader_queue)}"
        )
        self.join_leader_queue(ws, request)

    def handle_leave_request(self, request, ws):
        if not ws in self._remotes:
            return RoomManagementResponse(
                RoomResponseType.ERROR, None, None, None, None, "You are not in a room."
            )
        room_id, player_id, _ = self._remotes[ws].as_tuple()
        self.disconnect_socket(ws)
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(
                RoomResponseType.LEAVE_NOTICE,
                None,
                None,
                LeaveRoomNotice("Player requested leave."),
                None,
            )
        )

    def handle_stats_request(self, request, ws):
        total_players = sum([room.number_of_players() for room in self._rooms.values()])
        stats = StatsResponse(len(self._rooms), total_players, len(self._player_queue))
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(RoomResponseType.STATS, stats, None, None, None)
        )

    def handle_map_sample_request(self, request, ws):
        self._pending_room_management_responses[ws].put(
            RoomManagementResponse(
                RoomResponseType.MAP_SAMPLE,
                None,
                None,
                None,
                CachedMapRetrieval().map(),
            )
        )

    def remove_socket_from_queue(self, ws):
        player_queue = deque()
        removed = False
        for ts, element, request in self._player_queue:
            if element == ws:
                logger.info("Removed socket from queue.")
                removed = True
                continue
            player_queue.append((ts, element, request))
        if not removed:
            logger.warning("Socket not found in queue!")
        self._player_queue = player_queue

        follower_queue = deque()
        removed = False
        for ts, element, request in self._follower_queue:
            if element == ws:
                logger.info("Removed socket from follower queue.")
                removed = True
                continue
            follower_queue.append((ts, element, request))
        if not removed:
            logger.warning("Socket not found in follower queue!")
        self._follower_queue = follower_queue

        leader_queue = deque()
        removed = False
        for ts, element, request in self._leader_queue:
            if element == ws:
                logger.info("Removed socket from leader queue.")
                removed = True
                continue
            leader_queue.append((ts, element, request))
        if not removed:
            logger.warning("Socket not found in leader queue!")
        self._leader_queue = leader_queue

    def handle_cancel_request(self, request, ws):
        # Iterate through the queue of followers and leaders,
        # removing the given socket.
        print("Received queue cancel request from : " + str(ws))
        self.remove_socket_from_queue(ws)

    def handle_request(self, request: message_to_server.MessageToServer, ws):
        if request.type == message_to_server.MessageType.ROOM_MANAGEMENT:
            self.handle_room_request(request.room_request, ws)
        elif request.type == message_to_server.MessageType.TUTORIAL_REQUEST:
            self.handle_tutorial_request(request.tutorial_request, ws)
        elif request.type == message_to_server.MessageType.REPLAY_REQUEST:
            self.handle_replay_request(request.replay_request, ws)
        elif request.type == message_to_server.MessageType.SCENARIO_REQUEST:
            self.handle_scenario_request(request.scenario_request, ws)

    def handle_room_request(
        self, request: RoomManagementRequest, ws: web.WebSocketResponse
    ):
        if not ws in self._pending_room_management_responses:
            self._pending_room_management_responses[ws] = Queue()

        if request.type == RoomRequestType.JOIN:
            self.handle_join_request(request, ws)
        elif request.type == RoomRequestType.JOIN_FOLLOWER_ONLY:
            self.handle_follower_only_join_request(request, ws)
        elif request.type == RoomRequestType.JOIN_LEADER_ONLY:
            self.handle_leader_only_join_request(request, ws)
        elif request.type == RoomRequestType.LEAVE:
            self.handle_leave_request(request, ws)
        elif request.type == RoomRequestType.STATS:
            self.handle_stats_request(request, ws)
        elif request.type == RoomRequestType.CANCEL:
            self.handle_cancel_request(request, ws)
        elif request.type == RoomRequestType.MAP_SAMPLE:
            self.handle_map_sample_request(request, ws)
        else:
            logger.warning(f"Unknown request type: {request.type}")

    def drain_message(self, ws):
        if ws not in self._pending_room_management_responses:
            self._pending_room_management_responses[ws] = Queue()
        if not self._pending_room_management_responses[ws].empty():
            try:
                management_response = self._pending_room_management_responses[ws].get(
                    False
                )
                logger.debug(
                    f"Drained Room Management message type {management_response.type} for {ws}."
                )
                logger.debug(
                    f"Remaining messages in queue: {self._pending_room_management_responses[ws].qsize()}"
                )
                return message_from_server.RoomResponseFromServer(management_response)
            except queue.Empty:
                pass

        if ws not in self._pending_tutorial_messages:
            self._pending_tutorial_messages[ws] = Queue()
        if not self._pending_tutorial_messages[ws].empty():
            try:
                tutorial_response = self._pending_tutorial_messages[ws].get(False)
                logger.debug(
                    f"Drained tutorial response type {tutorial_response.type} for {ws}."
                )
                return message_from_server.TutorialResponseFromServer(tutorial_response)
            except queue.Empty:
                pass
        if ws not in self._pending_replay_messages:
            self._pending_replay_messages[ws] = Queue()
        if not self._pending_replay_messages[ws].empty():
            try:
                replay_response = self._pending_replay_messages[ws].get(False)
                logger.debug(
                    f"Drained replay response type {replay_response.type} for {ws}."
                )
                return message_from_server.ReplayResponseFromServer(replay_response)
            except queue.Empty:
                pass
        if ws not in self._pending_scenario_messages:
            self._pending_scenario_messages[ws] = Queue()
        if not self._pending_scenario_messages[ws].empty():
            try:
                scenario_response = self._pending_scenario_messages[ws].get(False)
                logger.info(
                    f"Drained scenario response type {scenario_response.type} for {ws}."
                )
                return message_from_server.ScenarioResponseFromServer(scenario_response)
            except queue.Empty:
                pass

        return None
