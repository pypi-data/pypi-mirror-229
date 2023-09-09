import logging
import threading
import time

import fire
import matplotlib.pyplot as plt
import nest_asyncio
import numpy as np
from viztracer import VizTracer

import cb2game.server.db_tools.db_utils as db_utils
from cb2game.pyclient.demos.follower_client import *
from cb2game.pyclient.demos.routing_leader_client import *
from cb2game.pyclient.endpoint_pair import EndpointPair
from cb2game.pyclient.game_endpoint import Action, Role
from cb2game.pyclient.local_game_coordinator import LocalGameCoordinator
from cb2game.server.config.config import ReadConfigOrDie
from cb2game.server.lobbies.open_lobby import OpenLobby
from cb2game.server.lobby import LobbyInfo, LobbyType

logger = logging.getLogger(__name__)


class PathfindingLeader(threading.Thread):
    def __init__(self, game=None):
        super().__init__()
        self.exc = None
        self.game = game

    def get_action(self, map, cards, turn_state, instructions, actors, feedback):
        if turn_state.turn != Role.LEADER:
            return Action.NoopAction()
        if has_instruction_available(instructions):
            # If the follower already has something to do, just end the turn.
            return Action.EndTurn()
        (leader, follower) = actors
        closest_card = get_next_card(cards, follower)
        if closest_card is None:
            # Just have the follower make random moves, hope something happens...
            return Action.SendInstruction(
                "random, random, random, random, random, random"
            )
        instruction = get_instruction_to_location(
            closest_card.prop_info.location, follower, map, cards, self.game
        )
        logger.info(f"Lead sending: {instruction}")
        return Action.SendInstruction(instruction)


class NaiveFollower(threading.Thread):
    def __init__(self, game):
        super().__init__()
        self.instructions_processed = set()
        self.actions = []
        self.exc = None
        self.game = game

    def get_action(self, map, cards, turn_state, instructions, actors, feedback):
        if len(self.actions) == 0:
            active_instruction = get_active_instruction(instructions)
            actions = []
            if active_instruction is not None:
                actions = actions_from_instruction(active_instruction.text)
            else:
                raise Exception(f"No active instruction. Instructions: {instructions}")
            if len(actions) == 0:
                actions = [Action.RandomMovementAction() for _ in range(5)]
            self.actions.extend(actions)
            if active_instruction is not None:
                self.actions.append(Action.InstructionDone(active_instruction.uuid))
                self.instructions_processed.add(active_instruction.uuid)
        if len(self.actions) > 0:
            action = self.actions[0]
            self.actions.pop(0)
            return action
        else:
            # Choose a random action.
            return Action.RandomMovementAction()


def PlayGame(coordinator, e_uuid="", log_to_db: bool = True, slow: bool = False):
    if len(e_uuid) > 0:
        game_name = coordinator.CreateGameFromDatabase(e_uuid)
    else:
        lobby = OpenLobby(
            LobbyInfo("Test Lobby", LobbyType.OPEN, "Unit test...", 40, 1, False)
        )
        game_name = coordinator.CreateGame(log_to_db=log_to_db, lobby=lobby)
    endpoint_pair = EndpointPair(coordinator, game_name)
    leader_agent = PathfindingLeader(endpoint_pair.leader())
    follower_agent = NaiveFollower(endpoint_pair.follower())
    endpoint_pair.initialize()
    (
        map,
        cards,
        turn_state,
        instructions,
        actors,
        live_feedback,
    ) = endpoint_pair.initial_state()
    while not endpoint_pair.over():
        if slow:
            time.sleep(0.5)
        if turn_state.turn == Role.LEADER:
            leader_action = leader_agent.get_action(
                map, cards, turn_state, instructions, actors, live_feedback
            )
            logger.info(f"Leader step({leader_action})")
            (
                map,
                cards,
                turn_state,
                instructions,
                actors,
                live_feedback,
            ) = endpoint_pair.step(leader_action)
        else:
            logger.info("=====================")
            action_mask = endpoint_pair.follower().action_mask()
            for action_code in Action.ActionCode:
                if action_code.value >= len(action_mask):
                    continue
                if action_mask[action_code.value]:
                    logger.info(f"Action {action_code} is available.")
            follower_action = follower_agent.get_action(
                map, cards, turn_state, instructions, actors, live_feedback
            )
            logger.info(f"Follower step({follower_action})")
            (
                map,
                cards,
                turn_state,
                instructions,
                actors,
                live_feedback,
            ) = endpoint_pair.step(follower_action)
    logger.info(
        f"Game over. Score: {endpoint_pair.score()}, Duration: {endpoint_pair.duration().total_seconds()}"
    )
    coordinator.Cleanup()
    return endpoint_pair.score(), endpoint_pair.duration().total_seconds()


def main(
    config_filepath="server/config/local-covers-config.yaml",
    event_uuid="",
    profile=False,
    num_games=10,
    slow: bool = False,
    log_to_db: bool = False,
):
    nest_asyncio.apply()
    # Disabling most logs improves performance by about 50ms per game.
    logging.basicConfig(level=logging.INFO)
    config = ReadConfigOrDie(config_filepath)
    db_utils.ConnectToDatabase(config)
    scores = []
    durations = []
    coordinator = LocalGameCoordinator(
        config, render_leader=False, render_follower=False
    )
    # If profile=True, play only 1 game, but import viztracer and save the trace to cb2-local.prof.
    if profile:
        with VizTracer(output_file="cb2-local-prof.json", tracer_entries=10000000):
            score, duration = PlayGame(coordinator, event_uuid)
        logger.info(f"Game over. Score: {score}, Duration: {duration}")
        return

    for i in range(num_games):
        logger.info(
            f"========================== STARTING GAME {i} =========================="
        )
        score, duration = PlayGame(
            coordinator, event_uuid, slow=slow, log_to_db=log_to_db
        )
        logger.info(f"Game over. Score: {score}, Duration: {duration}")
        scores.append(score)
        durations.append(duration)
    # Print out the scores.
    logger.info(f"Mean score: {np.mean(scores)}")
    logger.info(f"Mean duration: {np.mean(durations)}")

    # Plot a multi-figure diagram. On the left, scatter plot of game durations &
    # scores. On the right, show a histogram of scores.
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.scatter(durations, scores)
    ax1.set_xlabel("Duration")
    ax1.set_ylabel("Score")
    ax2.hist(scores)
    ax2.set_xlabel("Score")
    ax2.set_ylabel("Frequency")
    plt.show()


if __name__ == "__main__":
    fire.Fire(main)
