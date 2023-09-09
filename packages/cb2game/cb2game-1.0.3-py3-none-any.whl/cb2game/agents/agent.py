from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    pass


from cb2game.pyclient.game_endpoint import Action, GameState, Role


class RateLimitException(Exception):
    """Raised when the agent is rate limited by the implementation."""


class Agent(ABC):
    """CB2 agent interface.

    Implement this interface and register it in agents/config.py to create your own
    CB2 agent.

    Use agents/remote_agent.py to connect to a remote server (like CB2.ai), or
    agents/local_agent_pair.py for local self-training.
    """

    @abstractmethod
    def choose_action(
        self, game_state: GameState, action_mask: Optional[List[bool]] = None
    ) -> Action:
        """Chooses the next action to take, given a game state.

        Actions can be optionally masked out, by providing a mask. Agent may or
        may not support action_masking.  If None, then no masking is done.
        """
        ...

    @abstractmethod
    def role(self) -> Role:
        """Returns the role of the agent."""
        ...
