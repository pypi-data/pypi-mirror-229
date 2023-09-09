""" A Lobby that's open to all players. """
import logging
from datetime import datetime, timedelta
from typing import Tuple

from aiohttp import web

import cb2game.server.lobby as lobby
from cb2game.server.lobby import LobbyType
from cb2game.server.messages.rooms import RoomManagementRequest

logger = logging.getLogger(__name__)


class OpenLobby(lobby.Lobby):
    """Used to manage game rooms."""

    def __init__(self, lobby_info):
        # Call the superconstructor.
        super().__init__(lobby_info)

    # OVERRIDES Lobby.lobby_type()
    def lobby_type(self) -> LobbyType:
        return LobbyType.OPEN

    # OVERRIDES Lobby.get_leader_follower_match().
    def get_leader_follower_match(
        self,
    ) -> Tuple[web.WebSocketResponse, web.WebSocketResponse, str]:
        """Returns a tuple of (leader, follower, instruction_uuid) if there is a match, otherwise returns None.

        If neither client requested to play a game from a specific UUID,
        then UUID will be empty string.

        There are three queues of players: General players, follower-only,
        and leader-only players.
        General players must wait for either a follower or for 10 seconds to
        pass. Once 10 seconds have passed, they can match with other general
        players.
        Follower-only players must wait for a general player to become
        available. If a follower has waited for > 5m, they're expired from
        the queue.
        There's also a leader-only queue, which is similar to follower-only.

        If multiple matches are available, selects the most-experienced
        leader and least-experienced follower.

        Leaders and followers are removed from their respective queues. If
        either queue is empty, leaves the other untouched.
        """

        # If there's a leader in the leader queue and a follower in the follower queue, match them.
        if len(self._leader_queue) > 0 and len(self._follower_queue) > 0:
            (_, leader, l_e_uuid) = self._leader_queue.popleft()
            (_, follower, f_e_uuid) = self._follower_queue.popleft()
            if l_e_uuid:
                e_uuid = l_e_uuid
            elif f_e_uuid:
                e_uuid = f_e_uuid
            else:
                e_uuid = ""
            return leader, follower, e_uuid

        # If there's no general players, a match can't be made.
        if len(self._player_queue) < 1:
            return None, None, ""

        # If there's a leader and a general player, match them.
        if len(self._leader_queue) > 0 and len(self._player_queue) > 0:
            (_, leader, l_e_uuid) = self._leader_queue.popleft()
            (_, player, f_e_uuid) = self._player_queue.popleft()
            if l_e_uuid:
                e_uuid = l_e_uuid
            elif f_e_uuid:
                e_uuid = f_e_uuid
            else:
                e_uuid = ""
            return leader, player, e_uuid

        # If there's a follower waiting, match them with the first general player.
        if len(self._follower_queue) >= 1:
            (_, leader, l_e_uuid) = self._player_queue.popleft()
            (_, follower, f_e_uuid) = self._follower_queue.popleft()
            if l_e_uuid:
                e_uuid = l_e_uuid
            elif f_e_uuid:
                e_uuid = f_e_uuid
            else:
                e_uuid = ""
            return leader, follower, e_uuid

        # If there's no follower waiting, check if there's two general players...
        if len(self._player_queue) < 2:
            return (None, None, "")

        # If a general player has been waiting for >= 10 seconds with no follower, match them with another general player.
        (ts, _, _) = self._player_queue[0]
        if datetime.now() - ts > timedelta(seconds=1):
            (_, player1, e_uuid_1) = self._player_queue.popleft()
            (_, player2, e_uuid_2) = self._player_queue.popleft()
            # This is the main difference between this class and mturk lobby. If
            # two general players are matched, first one is given leader (rather
            # than choosing based on experience).
            leader, follower = (player1, player2)
            if e_uuid_1:
                e_uuid = e_uuid_1
            elif e_uuid_2:
                e_uuid = e_uuid_2
            else:
                e_uuid = ""
            if leader is None or follower is None:
                logger.warning(
                    "Could not assign leader and follower based on experience. Using random assignment."
                )
                return (player1, player2, e_uuid)
            return leader, follower, e_uuid
        return None, None

    # OVERRIDES Lobby.handle_join_request().
    def handle_join_request(
        self, request: RoomManagementRequest, ws: web.WebSocketResponse
    ) -> None:
        """Handles a join request from a client."""
        logger.info(f"Received join request from {ws}.")
        self.join_player_queue(ws, request)

    # Overrides Lobby.handle_replay_request()
    def handle_replay_request(
        self, request: RoomManagementRequest, ws: web.WebSocketResponse
    ) -> None:
        """Handles a request to join a replay room. In most lobbies, this should be ignored (except lobbies supporting replay)."""
        logger.warning(
            f"Received replay request from {str(ws)} in non-replay lobby. Ignoring."
        )
        self.boot_from_queue(ws)
        return
