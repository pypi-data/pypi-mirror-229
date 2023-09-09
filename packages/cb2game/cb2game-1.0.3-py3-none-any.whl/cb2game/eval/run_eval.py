import logging
import time
from datetime import datetime, timedelta
from typing import List

import fire
from tqdm import tqdm

from cb2game.agents.agent import Agent, RateLimitException, Role
from cb2game.agents.config import (
    AgentConfigData,
    LoadAgentFromConfig,
    ReadAgentConfigOrDie,
    SerializeAgentConfig,
)
from cb2game.eval.eval_schema import Eval, InstructionEvaluation, RunSource
from cb2game.pyclient.endpoint_pair import EndpointPair
from cb2game.pyclient.local_game_coordinator import LocalGameCoordinator
from cb2game.server.card import Card
from cb2game.server.config.config import Config, ReadServerConfigOrDie
from cb2game.server.db_tools.db_utils import ListGames
from cb2game.server.lobbies.open_lobby import OpenLobby
from cb2game.server.lobby_consts import LobbyInfo, LobbyType
from cb2game.server.messages.objective import ObjectiveMessage
from cb2game.server.messages.prop import PropType
from cb2game.server.messages.turn_state import TurnState
from cb2game.server.scenario_util import (
    GameStateFromScenario,
    ReconstructScenarioFromEvent,
)
from cb2game.server.schemas import base
from cb2game.server.schemas.event import Event, EventType
from cb2game.server.state_utils import (
    FOLLOWER_MOVES_PER_TURN,
    FOLLOWER_SECONDS_PER_TURN,
)
from cb2game.server.util import GetCommitHash, PackageVersion

logger = logging.getLogger(__name__)

# This is the default lobby name. Should equal the eval lobby defined in
# server/config/config.py. Must match the eval lobby on the remote server.
REMOTE_LOBBY_NAME = "eval-lobby"


def SwitchToDatabase(db):
    base.SetDatabaseByPath(db)
    base.ConnectDatabase()


def follower_eval_start(instruction: Event) -> Event:
    first_follower_move = (
        Event.select()
        .where(
            (Event.type == EventType.ACTION) & (Event.parent_event_id == instruction.id)
        )
        .order_by(Event.server_time)
        .first()
    )
    if first_follower_move is None:
        logger.info("No follower move found.")
        return None
    event_before = (
        Event.select()
        .where(
            (Event.game == first_follower_move.game)
            & (Event.server_time < first_follower_move.server_time)
        )
        .order_by(Event.server_time.desc())
        .first()
    )
    return event_before


def final_follower_move(instruction: Event) -> Event:
    last_follower_move = (
        Event.select()
        .where(
            (Event.type == EventType.ACTION) & (Event.parent_event_id == instruction.id)
        )
        .order_by(Event.server_time.desc())
        .first()
    )
    if last_follower_move is None:
        # No follower move found. Just get the INSTRUCTION_DONE event. Return null if
        # that doesn't exist either (instruction cancelled or game ended).
        instruction_complete_event = (
            Event.select()
            .where(
                (Event.type == EventType.INSTRUCTION_DONE)
                & (Event.parent_event_id == instruction.id)
            )
            .first()
        )
        return instruction_complete_event

    # Get the event after this one.
    event_after = (
        Event.select()
        .where(
            (Event.game == last_follower_move.game)
            & (Event.server_time > last_follower_move.server_time)
        )
        .order_by(Event.server_time)
        .first()
    )
    return event_after


def CompareCardSelections(a: List[Card], b: List[Card]) -> bool:
    selected_ids_a = set([card.id for card in a if card.selected])
    selected_ids_b = set([card.id for card in b if card.selected])
    return selected_ids_a == selected_ids_b


def InitPythonLogging():
    log_format = "[%(asctime)s] %(name)s %(levelname)s [%(module)s:%(funcName)s:%(lineno)d] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    logging.getLogger("peewee").setLevel(logging.INFO)


def RunEval(
    agent: Agent,
    output_prefix: str = "eval_",
    server_config_path: str = "",
    limit: int = -1,
    # Optional information about the agent that will be saved in the eval JSON output.
    agent_config: AgentConfigData = None,
):
    """Runs an eval against the given agent.

    Server configuration is required. This allows us to preserve the settings,
    software version, and lobby configuration that were used to collect the game
    data. Without this, an eval would be impossible to reproduce.

    Args:
        agent: The agent to run the eval against.
        output_prefix: The prefix to use for the output file.
        limit: The maximum number of instructions to evaluate. If -1, no limit.
        server_config_path: The path to the server config file.
    """
    if server_config_path == "":
        config = Config()
        logger.warning(
            f"Server config path not provided. Using default config. Database path: {config.data_directory()}"
        )
    else:
        config = ReadServerConfigOrDie(server_config_path)

    base.SetDatabase(config)
    base.ConnectDatabase()

    games = ListGames()
    game_ids = [game.id for game in games]
    instructions = Event.select().where(
        (Event.type == EventType.INSTRUCTION_SENT) & (Event.game_id << game_ids)
    )

    if limit >= 0:
        instructions = instructions.limit(limit)

    if instructions.count() == 0:
        print("No instructions found.")
        return

    # Create an eval run entry in the database.
    eval_run = Eval(
        run_source=RunSource.LOCAL,
        commit_version=GetCommitHash() or PackageVersion(),
        agent_config=SerializeAgentConfig(agent_config),
        agent_role=agent.role(),
        server_config=config.to_json(),
    )
    # This object will help us launch local games.
    coordinator = LocalGameCoordinator(
        config,
        render_leader=False,
        render_follower=False,
    )

    eval_lobby = OpenLobby(
        LobbyInfo(
            name="eval virtual lobby",
            type=LobbyType.OPEN,
            comment="Ephemeral lobby used for eval runs.",
            game_capacity=1,
            sound_clip_volume=0,
        )
    )

    agent_instructions_passed = []
    results = []
    for instruction in tqdm(instructions):
        try:
            objective = ObjectiveMessage.from_json(instruction.data)
            logger.info(
                f"Evaluating agent {agent_config.type} on instruction {instruction.id}"
            )
            logger.info(f"Instruction text: {objective.text}")
            if agent.role() == Role.LEADER:
                # Leader eval not yet supported.
                logger.info(f"Leader eval not yet supported.")
                return
            elif agent.role() == Role.FOLLOWER:
                eval_start_event = follower_eval_start(instruction)
                final_baseline_state = final_follower_move(instruction)
                if eval_start_event is None or final_baseline_state is None:
                    logger.info(
                        "Skipping instruction. Invalid start or end states. This could be due to the instruction being cancelled or the game ending."
                    )
                    continue

            # Create a local game to run the eval.
            game_name = coordinator.CreateGameFromDatabase(
                eval_start_event.id.hex, log_to_db=False, lobby=eval_lobby
            )
            # Due to a known bug (now patched) where TURN_STATE events were not
            # being logged, we need to force the current turn state to be at the
            # beginning of the follower's turn, with full moves and time.
            state_machine = coordinator._state_machine_driver(
                game_name
            ).state_machine()  # pylint: disable=protected-access
            state_machine._send_turn_state(
                TurnState(  # pylint: disable=protected-access
                    Role.FOLLOWER,
                    FOLLOWER_MOVES_PER_TURN,
                    1,  # As long as next turn isn't game over.
                    datetime.utcnow() + timedelta(seconds=FOLLOWER_SECONDS_PER_TURN),
                    datetime.utcnow(),
                    0,  # Let's start each eval with a score of zero.
                    0,
                    False,
                    0,
                )
            )
            endpoint_pair = EndpointPair(coordinator, game_name)
            endpoint_pair.initialize()
            game_state = endpoint_pair.initial_state()

            if game_state.turn_state.turn != agent.role():
                logger.error(
                    f"Agent role {agent.role()} does not match turn eval run state {game_state.turn_state.turn}"
                )
                continue

            # Keep running until the current turn is over. We check for this inside
            # the loop because the game state may change in the middle of the loop.
            agent_actions = []
            while not endpoint_pair.over():
                # If the turn is over, then the eval for this instruction is done.
                if game_state.turn_state.turn != agent.role():
                    break
                action = agent.choose_action(game_state)
                game_state = endpoint_pair.step(action)
                agent_actions.append(str(action))

            logger.info(f"Agent actions: {agent_actions}")

            # Now we have the agent's completed game state. We must compare it to
            # the baseline. Fetch the final game state after this instruction was
            # completed in the baseline game in the database.
            final_scenario, err = ReconstructScenarioFromEvent(final_baseline_state.id)
            final_baseline_state = GameStateFromScenario(final_scenario)

            # Compare the final game state to the human game state. See if the card
            # selections and scores match.
            final_agent_props = game_state.props
            final_agent_cards = [
                Card.FromProp(prop)
                for prop in final_agent_props
                if prop.prop_type == PropType.CARD
            ]
            final_agent_score = game_state.turn_state.score
            final_baseline_props = final_baseline_state.props
            final_baseline_cards = [
                Card.FromProp(prop)
                for prop in final_baseline_props
                if prop.prop_type == PropType.CARD
            ]
            final_baseline_score = final_baseline_state.turn_state.score
            card_selections_match = CompareCardSelections(
                final_agent_cards, final_baseline_cards
            )
            passed_instruction_eval = card_selections_match and (
                final_agent_score >= final_baseline_score
            )
            if passed_instruction_eval:
                agent_instructions_passed.append(instruction.id)
            results.append(
                InstructionEvaluation(
                    instruction_uuid=instruction.short_code,
                    agent_actions=str(agent_actions),
                    event_uuid=eval_start_event.id.hex,
                    success=passed_instruction_eval,
                )
            )
        except RateLimitException:
            logger.info(f"Rate limit error. Waiting 60 seconds.")
            results.append(
                InstructionEvaluation(
                    instruction_uuid=instruction.short_code,
                    agent_actions=str(agent_actions),
                    event_uuid=eval_start_event.id.hex,
                    success=False,
                    error="Rate limit error. Waiting 60 seconds.",
                )
            )
            time.sleep(60)
            continue
        except Exception as e:
            # Log the exception, with stack trace and instruction ID.
            logger.error(
                f"Exception in eval run {eval_run.id} for instruction {instruction.id}."
            )
            logger.error(e, exc_info=True)
            break

    # Save results to JSON file. See eval/eval_schema.py for the schema.
    eval_run.percent_passed = (
        (100 * len(agent_instructions_passed) / len(results)) if len(results) > 0 else 0
    )
    eval_run.total_instructions = len(results)
    eval_run.instruction_evals = results
    # Serialize the eval run to JSON.
    eval_run_json = eval_run.to_json()
    # Save the JSON to a file.
    with open(f"{output_prefix}{eval_run.id}.json", "w") as f:
        f.write(eval_run_json)
    logger.info(f"Eval run {eval_run.id} complete.")
    if len(results) > 0:
        logger.info(
            f"Instructions passed: {len(agent_instructions_passed)}. ({100 * len(agent_instructions_passed) / len(results)}%)"
        )
    logger.info(f"Total instructions: {len(results)}")


def main(
    agent_config: str,
    output_prefix: str = "eval_",
    server_config: str = "",
    limit: int = -1,
):
    InitPythonLogging()
    agent_config_data = ReadAgentConfigOrDie(agent_config)
    agent = LoadAgentFromConfig(agent_config_data)
    RunEval(
        agent,
        output_prefix,
        server_config,
        limit,
        agent_config_data,
    )


if __name__ == "__main__":
    fire.Fire(main)
