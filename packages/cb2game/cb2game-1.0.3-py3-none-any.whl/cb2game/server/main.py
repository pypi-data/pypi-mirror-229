import asyncio
import atexit
import base64
import dataclasses
import hashlib
import json
import logging
import multiprocessing as mp
import os
import pathlib
import queue
import statistics
import sys
import tempfile
import time
import warnings
import zipfile
from datetime import datetime, timedelta, timezone

from cb2game.server.util import PackageRoot, SafePasswordCompare

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""  # Hide pygame welcome message

import aiohttp
import cryptography
import fire
import orjson
import peewee
from aiohttp import web
from aiohttp_session import get_session, new_session, setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from dateutil import parser, tz
from playhouse.sqlite_ext import SqliteExtDatabase

import cb2game.server.db_tools.db_utils as db_utils
import cb2game.server.leaderboard as leaderboard
import cb2game.server.schemas as schemas
import cb2game.server.schemas.client_exception as client_exception_db
import cb2game.server.schemas.defaults as defaults
import cb2game.server.schemas.event as event_db
import cb2game.server.schemas.game as game_db
import cb2game.server.schemas.mturk as mturk
from cb2game.server.client_exception_logger import ClientExceptionLogger
from cb2game.server.config.config import GlobalConfig, InitGlobalConfig
from cb2game.server.google_authenticator import GoogleAuthenticator
from cb2game.server.lobby_consts import IsMturkLobby, LobbyType
from cb2game.server.lobby_utils import GetLobbies, GetLobby, InitializeLobbies
from cb2game.server.map_provider import MapGenerationTask, MapPoolSize
from cb2game.server.messages import message_from_server, message_to_server
from cb2game.server.messages.user_info import UserType
from cb2game.server.remote_table import (
    AddRemote,
    DeleteRemote,
    GetRemote,
    GetRemoteTable,
    LogConnectionEvent,
    Remote,
)
from cb2game.server.schemas import base
from cb2game.server.user_info_fetcher import UserInfoFetcher
from cb2game.server.util import HEARTBEAT_TIMEOUT_S, password_protected

routes = web.RouteTableDef()

# Lobby names.
MTURK_LOBBY = "mturk-lobby"
DEFAULT_LOBBY = "default"
OPEN_LOBBY = "open"
BOT_SANDBOX = "bot-sandbox"

logger = logging.getLogger()

google_authenticator = GoogleAuthenticator()
user_info_fetcher = UserInfoFetcher()
client_exception_logger = ClientExceptionLogger()


async def transmit(ws, message):
    remote = GetRemote(ws)
    if remote is None:
        return ValueError("Agent ID not found in remote table")

    remote.bytes_down += len(message)
    remote.last_message_down = time.time()

    try:
        await ws.send_str(message)
    except ConnectionResetError:
        pass


async def transmit_bytes(ws, message):
    remote = GetRemote(ws)
    if remote is None:
        return ValueError("Agent ID not found in remote table")

    remote.bytes_down += len(message)
    remote.last_message_down = time.time()

    try:
        await ws.send_str(message.decode("utf-8"))
    except ConnectionResetError:
        pass


@routes.get("/")
async def Index(request):
    return web.FileResponse(PackageRoot() / "server/www/index.html")


# Login form for password-protected backend URLs.
@routes.get("/login")
async def Login(request):
    session = await get_session(request)
    authenticated = session.get("authenticated", False)
    if authenticated:
        # Get the redirect URL from the "next" parameter.
        next_url = request.query.get("next", "/")
        return web.HTTPFound(next_url)
    config = GlobalConfig()
    if config:
        if len(config.server_password_sha512) == 0:
            next_url = request.query.get("next", "/")
            return web.HTTPFound(next_url)
    return web.FileResponse(PackageRoot() / "server/www/login.html")


# Authentication endpoint for password-protected backend URLs.
@routes.post("/auth")
async def Auth(request):
    session = await new_session(request)
    if session is None:
        return web.HTTPFound("/login")
    # Get the password from the HTTP Authorization header
    auth = request.headers.get("Authorization")
    if auth is None:
        return web.HTTPFound("/login")
    # Auth line should look like "Basic <base64-encoded password>"
    user_password_base64 = auth.split(" ")[-1]
    user_password = base64.b64decode(user_password_base64).decode("utf-8")
    if user_password is None:
        return web.HTTPUnauthorized(
            reason="Permission denied -- please provide a valid password using the password= parameter."
        )
    # The basic auth password is of the form user:password.
    password = user_password.split(":")[-1]

    # Check if the password is correct
    config = GlobalConfig()
    if config == None:
        return web.HTTPInternalServerError(reason="No config loaded.")
    password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
    if not SafePasswordCompare(config.server_password_sha512, password_hash):
        return web.HTTPUnauthorized(reason="Permission denied -- invalid password.")

    # Create a session cookie with the IP address and date.
    session["authenticated"] = True
    session["ip"] = request.remote
    session["expires"] = time.time() + 60 * 60 * 24 * 7  # 1 week
    session.changed()
    return web.HTTPFound("/")


@routes.get("/play")
async def GamePage(request):
    return web.FileResponse(PackageRoot() / "server/www/WebGL/index.html")


@routes.get("/consent-form")
async def ConsentForm(request):
    return web.FileResponse(PackageRoot() / "server/www/pdfs/consent-form.pdf")


@routes.get("/rules")
async def Rules(request):
    return web.FileResponse(PackageRoot() / "server/www/rules.html")


@routes.get("/payout")
async def Rules(request):
    return web.FileResponse(PackageRoot() / "server/www/payout.html")


@routes.get("/example_sets")
async def Rules(request):
    return web.FileResponse(PackageRoot() / "server/www/example_sets.html")


@routes.get("/oneoff")
async def OneoffComp(request):
    return web.FileResponse(PackageRoot() / "server/www/oneoff.html")


@routes.get("/follower-model-study")
async def TaskPage(request):
    return web.FileResponse(PackageRoot() / "server/www/follower-model-study.html")


@routes.get("/leader-model-study")
async def TaskPage(request):
    return web.FileResponse(PackageRoot() / "server/www/leader-model-study.html")


@routes.get("/main-study")
async def TaskPage(request):
    return web.FileResponse(PackageRoot() / "server/www/main-study.html")


@routes.get("/mturk-task")
async def TaskPage(request):
    return web.FileResponse(PackageRoot() / "server/www/mturk-task.html")


@routes.get("/follower-qual")
async def TaskPage(request):
    return web.FileResponse(PackageRoot() / "server/www/follower-qual.html")


@routes.get("/leader-qual")
async def TaskPage(request):
    return web.FileResponse(PackageRoot() / "server/www/leader-qual.html")


@routes.get("/changelist")
async def Changelist(request):
    return web.FileResponse(PackageRoot() / "server/www/changelist.html")


@routes.get("/privacy")
async def Privacy(request):
    return web.FileResponse(PackageRoot() / "server/www/privacy-policy.html")


@routes.get("/view/dashboard")
@password_protected
async def Dashboard(request):
    return web.FileResponse(PackageRoot() / "server/www/dashboard.html")


@routes.get("/images/{filename}")
async def Images(request):
    if not request.match_info.get("filename"):
        return web.HTTPNotFound()
    return web.FileResponse(
        PackageRoot() / f"server/www/images/{request.match_info['filename']}"
    )


@routes.get("/css/{filename}")
async def css(request):
    if not request.match_info.get("filename"):
        return web.HTTPNotFound()
    return web.FileResponse(
        PackageRoot() / f"server/www/css/{request.match_info['filename']}"
    )


@routes.get("/js/{filename}")
async def Js(request):
    if not request.match_info.get("filename"):
        return web.HTTPNotFound()
    return web.FileResponse(
        PackageRoot() / f"server/www/js/{request.match_info['filename']}"
    )


def JsonFromEvent(event: event_db.Event):
    # For convenience, convert timestamps to US eastern time.
    NYC = tz.gettz("America/New_York")
    return {
        "id": event.id.hex,
        "time": str(event.server_time.replace(tzinfo=tz.tzutc()).astimezone(NYC)),
        "turn_number": event.turn_number,
        "tick": event.tick,
        "type": event_db.EventType(event.type).name,
        "role": event.role,
        "origin": event.origin,
        "short_code": event.short_code,
        "location": str(event.location),
        "orientation": event.orientation,
        "data": event.data,
        "parent": event.parent_event.id.hex if event.parent_event is not None else None,
    }


def LobbyStatus(player_lobby):
    remote_table = GetRemoteTable()
    player_queue = [str(remote_table[x]) for _, x, _ in player_lobby.player_queue()]
    follower_queue = [str(remote_table[x]) for _, x, _ in player_lobby.follower_queue()]
    leader_queue = [str(remote_table[x]) for _, x, _ in player_lobby.leader_queue()]

    remotes = [
        GetRemote(ws) for ws in remote_table if player_lobby.socket_info(ws) is not None
    ]
    remote_infos = [
        {
            "hashed_ip": ws.hashed_ip,
            "time_offset": ws.time_offset,
            "latency": ws.latency,
            "bytes_up": ws.bytes_up,
            "bytes_down": ws.bytes_down,
            "mturk_id_hash": hashlib.md5(ws.mturk_id.encode("utf-8")).hexdigest()
            if ws.mturk_id
            else None,
            "user_type": ws.user_type,
            "uuid": ws.uuid,
        }
        for ws in remotes
    ]

    latency_monitor = player_lobby.latency_monitor()
    return {
        "type": repr(player_lobby.lobby_type()),
        "comment": player_lobby.lobby_comment(),
        "number_rooms": len(player_lobby.room_ids()),
        "hash": hash(player_lobby),
        "lobby_remotes": remote_infos,
        "rooms": [
            player_lobby.get_room(room_id).state()
            for room_id in player_lobby.room_ids()
        ],
        "player_queue": player_queue,
        "follower_queue": follower_queue,
        "leader_queue": leader_queue,
        "room_debug_info": [
            player_lobby.get_room(room_id).debug_status()
            for room_id in player_lobby.room_ids()
        ],
        "bucket_latencies": latency_monitor.bucket_latencies(),
        "bucket_timestamps": latency_monitor.bucket_timestamps(),
    }


@routes.get("/status")
@password_protected
async def Status(request):
    start_time = time.time()
    global assets_map
    remote_table = GetRemoteTable()
    lobbies = GetLobbies()
    remotes = [GetRemote(ws) for ws in remote_table]
    remote_infos = [
        {
            "hashed_ip": ws.hashed_ip,
            "time_offset": ws.time_offset,
            "latency": ws.latency,
            "bytes_up": ws.bytes_up,
            "bytes_down": ws.bytes_down,
            "mturk_id_hash": hashlib.md5(ws.mturk_id.encode("utf-8")).hexdigest()
            if ws.mturk_id
            else None,
            "user_type": ws.user_type,
            "uuid": ws.uuid,
        }
        for ws in remotes
    ]
    status = {
        "assets": assets_map,
        "map_cache_size": MapPoolSize(),
        "remotes": remote_infos,
        "lobbies": {},
    }
    for lobby in lobbies:
        logger.info(
            f"Getting status for lobby {lobby.lobby_name()}. hash: {hash(lobby)}"
        )
        status["lobbies"][lobby.lobby_name()] = LobbyStatus(lobby)
    pretty_dumper = lambda x: orjson.dumps(
        x, option=orjson.OPT_NAIVE_UTC | orjson.OPT_INDENT_2
    ).decode("utf-8")
    logger.info(f"Status request took {time.time() - start_time} seconds")
    return web.json_response(status, dumps=pretty_dumper)


@routes.get("/data/username_from_id/{user_id}")
async def GetUsername(request):
    user_id = request.match_info.get("user_id")
    if not user_id:
        return web.HTTPNotFound()
    hashed_id = (
        hashlib.md5(user_id.encode("utf-8")).hexdigest(),
    )  # Worker ID is PII, so only save the hash.
    worker_select = mturk.Worker.select().where(mturk.Worker.hashed_id == hashed_id)
    if worker_select.count() != 1:
        return web.HTTPNotFound()
    worker = worker_select.get()
    username = leaderboard.LookupUsername(worker)
    return web.json_response({"username": username})


@routes.get("/data/username_from_hash/{hashed_id}")
async def GetUsername(request):
    hashed_id = request.match_info.get("hashed_id")
    if not hashed_id:
        return web.HTTPNotFound()

    worker_select = mturk.Worker.select().where(mturk.Worker.hashed_id == hashed_id)
    if worker_select.count() != 1:
        return web.HTTPNotFound()
    worker = worker_select.get()
    username = leaderboard.LookupUsername(worker)
    return web.json_response({"username": username})


@routes.get("/data/leaderboard")
async def MessagesFromServer(request):
    lobby_name = ""
    lobby_type = LobbyType.NONE
    only_follower_bot_games = False
    if "lobby_name" in request.query:
        lobby_name = request.query["lobby_name"]
    if "lobby_type" in request.query:
        lobby_type_string = request.query["lobby_type"]
        lobby_type = LobbyType(int(lobby_type_string))
    if "only_follower_bot_games" in request.query:
        only_follower_bot_games = (
            request.query["only_follower_bot_games"].lower() == "true"
        )
    board = leaderboard.GetLeaderboard(lobby_name, lobby_type, only_follower_bot_games)
    leaderboard_entries = []
    logger.info(f"Leaderboard for {lobby_name} {lobby_type} has {len(board)} entries")
    for i, entry in enumerate(board):
        leader_name = entry.leader_name
        follower_name = entry.follower_name
        if leader_name == None:
            leader_name = ""
        if follower_name == None:
            follower_name = ""
        logger.info(
            f"{i:3}: scr: {entry.score} ldr: {leader_name} flwr: {follower_name} time: {entry.time}"
        )
        entry = {
            "time": str(entry.time.date()),
            "score": entry.score,
            "leader": leader_name,
            "follower": follower_name,
            "lobby_name": entry.lobby_name,
            "lobby_type": entry.lobby_type,
        }
        leaderboard_entries.append(entry)
    return web.json_response(leaderboard_entries)


download_requested = False
download_file_path = ""
download_status = {
    "status": "idle",
    "log": [],
}


async def ExceptionSaver(lobbies, config):
    while True:
        try:
            await asyncio.sleep(config.exception_log_interval)
            # Check mturk lobbies to see if there are any active games.
            active_game = False
            for lob in lobbies:
                if not IsMturkLobby(lob.lobby_type()):
                    continue
                if len(lob.room_ids()) > 0:
                    active_game = True
                    break
            if not active_game:
                client_exception_logger.save_exceptions_to_db()
        except Exception as e:
            logger.exception(e)


async def DataDownloader(lobbies):
    global download_requested
    global download_status
    global download_file_path
    download_process = None
    download_time_started = None
    download_path = mp.Queue()
    logs = mp.Queue()
    NYC = tz.gettz("America/New_York")
    timestamp = lambda: datetime.now(NYC).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = lambda x: download_status["log"].append(f"{timestamp()}: {x}")
    while True:
        await asyncio.sleep(1)

        if not download_requested:
            continue

        if download_process is not None:
            try:
                log = logs.get(False)
                download_status["log"].append(log)
            except queue.Empty:
                pass

        if download_process is not None and not download_process.is_alive():
            try:
                download_file_path = download_path.get(True, 15)
                log_entry(f"Download ready in temp file at {download_file_path}.")
                download_status["status"] = "ready"
                download_requested = False
                download_process.terminate()
                download_process = None
                download_path = mp.Queue()
                logs = mp.Queue()
            except queue.Empty:
                download_process.terminate()
                download_process = None
                download_status["status"] = "error"
                download_requested = False
                download_file_path = ""
                download_time_started = None
                download_path = mp.Queue()
                logs = mp.Queue()
                download_status["log"] = []

        if download_process is not None and download_process.is_alive():
            # If the process is still running, but we've waited 5 minutes, kill it.
            if (datetime.now() - download_time_started).total_seconds() > 300:
                log_entry("Download process timed out.")
                download_process.terminate()
                download_process = None
                download_status["status"] = "error"
                download_requested = False
                download_file_path = ""
                download_time_started = None
                download_path = mp.Queue()
                logs = mp.Queue()
                download_status["log"] = []
                continue

        # Check mturk lobbies to see if there are any active games.
        for lobby in lobbies:
            if not IsMturkLobby(lobby.lobby_type()):
                continue
            if len(lobby.room_ids()) > 0:
                download_status["status"] = "busy"
                break
        # Don't start downloads if someone is actively playing a game.
        if download_status["status"] == "busy":
            log_entry(
                f"Waiting on {len(lobby.room_ids())} active games to finish before downloading."
            )
            await asyncio.sleep(10)
            continue

        if download_process is None and download_status["status"] in ["done", "idle"]:
            download_process = mp.Process(
                target=GatherDataForDownload, args=(GlobalConfig(), download_path, logs)
            )
            download_process.start()
            download_status["status"] = "preparing"
            download_status["log"] = []
            download_time_started = datetime.now()


def GatherDataForDownload(config, response, logs):
    """Zips up player data for download in a separate thread. Param response is a queue to put the zip file path into."""
    NYC = tz.gettz("America/New_York")
    timestamp = lambda: datetime.now(NYC).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = lambda x: logs.put(f"{timestamp()}: {x}")
    database = SqliteExtDatabase(
        config.database_path(),
        pragmas=[
            ("cache_size", -1024 * 64),  # 64MB page-cache.
            ("journal_mode", "wal"),  # Use WAL-mode (you should always use this!).
            ("foreign_keys", 1),
        ],
    )
    log_entry(f"Starting...")
    log_entry("Compressing to zip...")
    download_file = tempfile.NamedTemporaryFile(
        delete=False, prefix="game_data_", suffix=".zip"
    )
    download_file_path = download_file.name
    with zipfile.ZipFile(download_file, "a", False) as zip_file:
        with open(config.database_path(), "rb") as db_file:
            zip_file.writestr("game_data.db", db_file.read())
            log_entry(f"DB file added to download ZIP.")
    download_file.close()
    log_entry("Zip file written to disk.")
    log_entry(f"Download ready in temp file at {download_file_path}.")
    response.put(download_file_path)


@routes.get("/data/download_status")
@password_protected
async def DownloadStatus(request):
    global download_status
    return web.json_response(download_status)


files_to_clean = []  # [file_path_1: str, ...]


def CleanupDownloadFiles():
    # Cleanup temporary download files that have been sitting around
    global files_to_clean
    logger.info("Deleting temporary files...")
    for file in files_to_clean:
        logger.info(f"Deleting: {file}")
        os.remove(file)


def SaveClientExceptionsToDB():
    logger.info(
        f"Saving {len(client_exception_logger.pending_exceptions())} client exceptions to DB..."
    )
    client_exception_logger.save_exceptions_to_db()


@routes.get("/data/download_retrieve")
@password_protected
async def RetrieveData(request):
    global download_status
    global download_file_path
    global files_to_clean
    NYC = tz.gettz("America/New_York")
    timestamp = lambda: datetime.now(NYC).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = lambda x: download_status["log"].append(f"{timestamp()}: {x}")
    # Make sure download_file_path is a file.
    if not os.path.isfile(download_file_path):
        log_entry("Retrieval attempted, but no download available.")
        return web.HTTPNotFound()
    log_entry("Retrieved download.")
    download_status["status"] = "done"
    local_download_file_path = download_file_path
    download_file_path = ""
    files_to_clean.append(local_download_file_path)
    return web.FileResponse(
        local_download_file_path,
        headers={
            "Content-Disposition": f"attachment;filename={os.path.basename(download_file_path)}"
        },
    )


@routes.get("/data/download")
@password_protected
async def DataDownloadStart(request):
    global download_requested
    download_requested = True
    return web.FileResponse(PackageRoot() / "server/www/download.html")


@routes.get("/data/game-list")
@password_protected
async def GameList(request):
    start_time = time.time()
    # Default to 100 games to reduce load on server.
    limit_to_100 = True
    request_query = json.loads(request.query.get("request", "{}"))
    if "all" in request_query:
        if request_query["all"]:
            limit_to_100 = False
    # Get search data from request.
    games = game_db.Game.select().join(
        mturk.Worker,
        join_type=peewee.JOIN.LEFT_OUTER,
        on=(
            (game_db.Game.leader == mturk.Worker.id)
            or (game_db.Game.follower == mturk.Worker.id)
        ),
    )
    if limit_to_100:
        games = games.limit(100)
    games = games.order_by(game_db.Game.id.desc())
    response = []
    # For convenience, convert timestamps to US eastern time.
    NYC = tz.gettz("America/New_York")
    # Parse the "searches" array of json objects.
    # w2_request = request.query.getall("request", {"searches": []})
    # Get the searches array from post data and confirm it matches.

    # Print the request query.
    searchRequest = json.loads(request.query.get("request", "{}"))
    searches = searchRequest.get("search", [])

    for search in searches:
        if search["field"] in ["leader", "follower"]:
            logger.info(
                f"Hashing value: {search['value']} and len: {len(search['value'])}"
            )
            search["value-md5"] = hashlib.md5(
                search["value"].encode("utf-8")
            ).hexdigest()
    for game in games:
        search_found = False
        for search in searches:
            if search["field"] == "id":
                if search["value"] in str(game.id):
                    search_found = True
            elif search["field"] == "leader":
                if game.leader:
                    if search["value"] in game.leader.hashed_id or (
                        search["value-md5"] == game.leader.hashed_id
                    ):
                        search_found = True
            elif search["field"] == "follower":
                if game.follower:
                    if search["value"] in game.follower.hashed_id or (
                        search["value-md5"] == game.follower.hashed_id
                    ):
                        search_found = True
        if not search_found and len(searches) > 0:
            continue
        response.append(
            {
                "id": game.id,
                "type": game.type,
                "leader": game.leader.hashed_id if game.leader else None,
                "follower": game.follower.hashed_id if game.follower else None,
                "score": game.score,
                "turns": game.number_turns,
                "start_time": str(
                    game.start_time.replace(tzinfo=tz.tzutc()).astimezone(NYC)
                ),
                "duration": str(game.end_time - game.start_time),
                "completed": game.completed,
                # Calculating this is too expensive per-game. Running it on
                # every game entry (done here) actually pauses running games
                # for 2 seconds.
                #
                # "research_valid": db_utils.IsGameResearchData(game),
                "kvals": game.kvals,
            }
        )
    logger.info(f"Number of search results: {len(response)}")
    end_time = time.time()
    logger.info(f"Search took {end_time - start_time} seconds.")
    return web.json_response(response)


@routes.get("/data/client-exception-list")
@password_protected
async def ClientExceptionList(request):
    exceptions = client_exception_db.ClientException.select().order_by(
        client_exception_db.ClientException.date.desc()
    )
    responses = [
        {
            "id": exception.id.hex,
            "game_id": exception.game_id,
            "role": exception.role,
            "date": str(exception.date),
            "bug_report": exception.bug_report,
            "condition": exception.condition,
            "stack_trace": exception.stack_trace,
            "type": exception.type,
        }
        for exception in exceptions
    ]
    return web.json_response(responses)


@routes.get("/view/client-exceptions")
@password_protected
async def ClientExceptionViewer(request):
    return web.FileResponse(PackageRoot() / "server/www/exceptions_viewer.html")


@routes.get("/view/games")
@password_protected
async def GamesViewer(request):
    return web.FileResponse(PackageRoot() / "server/www/games_viewer.html")


@routes.get("/view/game/{game_id}")
@password_protected
async def GameViewer(request):
    # Extract the game_id from the request.
    return web.FileResponse(PackageRoot() / "server/www/game_viewer.html")


@routes.get("/data/config")
async def GetConfig(request):
    pretty_dumper = lambda x: orjson.dumps(
        x, option=orjson.OPT_NAIVE_UTC | orjson.OPT_INDENT_2
    ).decode("utf-8")
    return web.json_response(GlobalConfig(), dumps=pretty_dumper)


@routes.get("/view/stats")
@password_protected
async def Stats(request):
    return web.FileResponse(PackageRoot() / "server/www/stats.html")


@routes.get("/data/turns/{game_id}")
@password_protected
async def GameData(request):
    game_id = request.match_info.get("game_id")
    game_turn_events = event_db.Event.select().where(
        event_db.Event.game == game_id,
        event_db.Event.type == event_db.EventType.START_OF_TURN,
    )
    turns = []
    for event in game_turn_events:
        turns.append(JsonFromEvent(event))
    return web.json_response(turns)


@routes.get("/data/events/{game_id}")
@password_protected
async def EventData(request):
    """HTTP endpoint to fetch all events for a particular game."""
    game_id = request.match_info.get("game_id")
    events = (
        event_db.Event.select()
        .where(event_db.Event.game == game_id)
        .order_by(event_db.Event.server_time)
    )
    json_events = [JsonFromEvent(event) for event in events]
    return web.json_response(json_events)


@routes.get("/data/instructions/{game_id}")
@password_protected
async def InstructionData(request):
    """HTTP endpoint to fetch all instructions for a particular game."""
    game_id = request.match_info.get("game_id")
    events = (
        event_db.Event.select()
        .where(
            event_db.Event.game == game_id,
            event_db.Event.type == event_db.EventType.INSTRUCTION_SENT,
        )
        .order_by(event_db.Event.server_time)
    )
    json_events = [JsonFromEvent(event) for event in events]
    return web.json_response(json_events)


@routes.get("/data/game_live_feedback/{game_id}")
@password_protected
async def GetGameLiveFeedback(request):
    """HTTP endpoint to fetch all live feedback for a particular game."""
    game_id = request.match_info.get("game_id")

    game_events = (
        event_db.Event.select()
        .where(event_db.Event.game == game_id)
        .join(event_db.Event)
    )

    # Fetch all instructions from this game. Then, check if at least 75% of them have live feedback.
    instructions = game_events.where(
        event_db.Event.type == event_db.EventType.INSTRUCTION_SENT
    )
    if len(instructions) == 0:
        return web.json_response(
            {
                "game_id": game_id,
                "total_instructions": 0,
                "total_live_feedback": 0,
                "percent": 0,
            }
        )

    # Now fetch all live feedback for this game.
    live_feedback = game_events.where(
        event_db.Event.type == event_db.EventType.LIVE_FEEDBACK
    )

    # Now, check if at least 75% of the instructions have live feedback.
    live_feedback_uuids = []
    for event in live_feedback:
        move_event = event.parent_event
        instruction_event = move_event.parent_event
        instruction_uuid = instruction_event.short_code
        live_feedback_uuids.append(instruction_uuid)

    instruction_uuids = set([event.short_code for event in instructions])
    live_feedback_uuids = set(live_feedback_uuids)

    total_instructions = len(instruction_uuids)
    total_live_feedback = len(live_feedback_uuids)
    response = {
        "game_id": game_id,
        "total_instructions": total_instructions,
        "total_live_feedback": total_live_feedback,
        "percent": total_live_feedback / total_instructions,
    }
    return web.json_response(response)


@routes.get("/data/instruction/{i_uuid}")
@password_protected
async def InstructionFromUuid(request):
    """HTTP endpoint to fetch an instruction from its UUID. Note that this is the in-game state machine UUID, not the database UUID."""
    instruction_uuid = request.match_info.get("i_uuid")
    instruction = (
        event_db.Event.select()
        .where(event_db.Event.short_code == instruction_uuid)
        .get()
    )
    tz.gettz("America/New_York")
    return web.json_response(
        instruction.dict(),
        dumps=lambda x: orjson.dumps(
            x, option=orjson.OPT_NAIVE_UTC | orjson.OPT_INDENT_2
        ).decode("utf-8"),
    )


@routes.get("/data/moves_for_instruction/{i_uuid}")
@password_protected
async def MovesForInstruction(request):
    instruction_uuid = request.match_info.get("i_uuid")
    instruction = (
        event_db.Event.select()
        .where(
            event_db.Event.type == event_db.EventType.INSTRUCTION_SENT,
            event_db.Event.short_code == instruction_uuid,
        )
        .get()
    )
    event_uuid = instruction.id
    # Select moves with parent_event = event_uuid
    moves = (
        event_db.Event.select()
        .where(event_db.Event.parent_event == event_uuid)
        .order_by(event_db.Event.server_time)
    )

    json_responses = [JsonFromEvent(event) for event in moves]
    return web.json_response(
        json_responses,
        dumps=lambda x: orjson.dumps(
            x, option=orjson.OPT_NAIVE_UTC | orjson.OPT_INDENT_2
        ).decode("utf-8"),
    )


@routes.get("/data/stats")
@password_protected
async def stats(request):
    games = db_utils.ListAnalysisGames(GlobalConfig())
    post_data = request.query.get("request", None)
    try:
        post_data = json.loads(post_data)
    except Exception as e:
        logger.info(f"Unable to parse JSON: {post_data}. Error: {e}")
    from_game_id = 0
    if len(games) > 0:
        to_game_id = max([game.id for game in games])
    else:
        to_game_id = 0
    if post_data:
        from_game_id = post_data.get("from_game_id", 0)
        to_game_id = post_data.get("to_game_id", 0)
    try:
        from_game_id = int(from_game_id)
        to_game_id = int(to_game_id)
        if (from_game_id > 0) or (to_game_id > 0) and (from_game_id < to_game_id):
            games = [game for game in games if from_game_id <= game.id <= to_game_id]
            logger.info(
                f"Filtered games to those >= game {from_game_id} and <= {to_game_id}. Remaining: {len(games)}"
            )
    except ValueError:
        logger.info(f"Invalid game IDs: {from_game_id} and {to_game_id}")
    durations = []
    scores = []
    instruction_counts = []
    instructions = []
    instruction_move_counts = []
    vocab = set()
    for game in games:
        game_events = event_db.Event.select().where(event_db.Event.game == game.id)
        instructions = game_events.where(
            event_db.Event.type == event_db.EventType.INSTRUCTION_SENT
        )
        for event in instructions:
            moves = game_events.where(
                event_db.Event.type == event_db.EventType.ACTION,
                event_db.Event.parent_event == event.id,
            )
            instruction_move_counts.append(moves.count())
            instruction_text = orjson.loads(event.data)["text"]
            instructions.append(instruction_text)
            words = instruction_text.split(" ")
            vocab.extend(words)
        duration = (game.end_time - game.start_time).total_seconds()
        score = game.score
        durations.append(duration)
        scores.append(score)
        instruction_counts.append(instructions.count())

    instruction_word_count = [
        len(instruction.split(" ")) for instruction in instructions
    ]

    json_stats = []

    if len(games) == 0:
        json_stats.append(
            {
                "name": "Games",
                "count": 0,
            }
        )
        return web.json_response(json_stats)

    json_stats.append(
        {
            "name": "Total Game Time(m:s)",
            "mean": str(timedelta(seconds=statistics.mean(durations))),
            "median": str(timedelta(seconds=statistics.median(durations))),
            "max": str(timedelta(seconds=max(durations))),
        }
    )

    json_stats.append(
        {
            "name": "Score",
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "max": max(scores),
        }
    )

    json_stats.append(
        {
            "name": "Instructions/Game",
            "mean": statistics.mean(instruction_counts),
            "median": statistics.median(instruction_counts),
            "max": max(instruction_counts),
        }
    )

    json_stats.append(
        {
            "name": "Tokens/Instruction",
            "mean": statistics.mean(instruction_word_count),
            "median": statistics.median(instruction_word_count),
            "max": max(instruction_word_count),
        }
    )

    json_stats.append(
        {
            "name": "Follower Actions/Instruction",
            "mean": statistics.mean(instruction_move_counts),
            "median": statistics.median(instruction_move_counts),
            "max": max(instruction_move_counts),
        }
    )

    json_stats.append({"name": "Games", "count": len(games)})

    json_stats.append({"name": "Vocabulary Size", "count": len(vocab)})

    game_outcomes = {}
    mturk_games = db_utils.ListMturkGames()
    logger.info(f"Number of games total: {len(mturk_games)}")
    total_config_games = 0
    for game in mturk_games:
        if db_utils.IsConfigGame(GlobalConfig(), game):
            logger.info(f"Game {game.id} is a config game")
            total_config_games += 1
            game_diagnosis = db_utils.DiagnoseGame(game)
            if (
                game_diagnosis
                == db_utils.GameDiagnosis.HIGH_PERCENT_INSTRUCTIONS_INCOMPLETE
            ):
                logger.info(f"Game {game.id} is incomplete")
            if game_diagnosis not in game_outcomes:
                game_outcomes[game_diagnosis] = 0
            game_outcomes[game_diagnosis] += 1
        else:
            logger.info(f"Game {game.id} is not config data")

    for game_diagnosis, count in game_outcomes.items():
        json_stats.append({"name": game_diagnosis.name, "count": count})

    json_stats.append(
        {"name": "Total MTurk Games in this config", "count": total_config_games}
    )

    return web.json_response(json_stats)


async def stream_game_state(request, ws, lobby):
    was_in_room = False
    remote = GetRemote(ws)
    remote.last_ping = datetime.now(timezone.utc)
    last_loop = time.time()
    menu_options_updated = False  # Whether the menu options have been transmitted.
    while not ws.closed:
        await asyncio.sleep(0)
        poll_period = time.time() - last_loop
        if (poll_period) > 0.2:
            logging.warning(
                f"Transmit socket for iphash {remote.hashed_ip} port {remote.client_port}, slow poll period of {poll_period}s"
            )
        last_loop = time.time()
        # If not in a room, drain messages from the room manager.
        message = lobby.drain_message(ws)
        if message is not None:
            await transmit_bytes(ws, orjson.dumps(message, option=orjson.OPT_NAIVE_UTC))

        # If the menu options have been updated, send them to the client.
        if not menu_options_updated:
            menu_options_updated = True
            message = message_from_server.MenuOptionsFromServer(lobby.menu_options(ws))
            # Wait 10ms first,
            await transmit_bytes(ws, orjson.dumps(message, option=orjson.OPT_NAIVE_UTC))

        # Handle any authentication confirmations.
        confirmations = google_authenticator.fill_auth_confirmations(ws)
        if len(confirmations) > 0:
            # If a user recently authenticated, the menu options may have changed.
            menu_options_updated = False
            for confirmation in confirmations:
                message = message_from_server.GoogleAuthConfirmationFromServer(
                    confirmation
                )
                await transmit_bytes(
                    ws, orjson.dumps(message, option=orjson.OPT_NAIVE_UTC)
                )

        # Fill userinfo responses.
        userinfo_responses = user_info_fetcher.fill_user_infos(ws)
        if len(userinfo_responses) > 0:
            for userinfo_response in userinfo_responses:
                message = message_from_server.UserInfoFromServer(userinfo_response)
                logger.info(f"message: {message}")
                await transmit_bytes(
                    ws, orjson.dumps(message, option=orjson.OPT_NAIVE_UTC)
                )

        if not lobby.socket_in_room(ws):
            if was_in_room:
                logger.info(
                    f"Socket has disappeared after initialization. Ending connection."
                )
                await ws.close()
                return
            continue

        (room_id, player_id, role) = lobby.socket_info(ws).as_tuple()
        room = lobby.get_room(room_id)

        if room is None:
            logger.warning(
                f"Room does not exist but lobby.socket_in_room(ws) returned true."
            )
            continue

        if not was_in_room:
            was_in_room = True
            # Make sure we drain pending room manager commands here with sleeps to ensure the client has time to switch scenes.
            # await asyncio.sleep(1.0)
            message = lobby.drain_message(ws)
            if message is not None:
                await transmit_bytes(
                    ws,
                    orjson.dumps(
                        message,
                        option=orjson.OPT_NAIVE_UTC | orjson.OPT_PASSTHROUGH_DATETIME,
                        default=datetime.isoformat,
                    ),
                )
            # await asyncio.sleep(1.0)
            continue

        # Send a ping every 10 seconds.
        if (datetime.now(timezone.utc) - remote.last_ping).total_seconds() > 10.0:
            remote.last_ping = datetime.now(timezone.utc)
            await transmit_bytes(
                ws,
                orjson.dumps(
                    message_from_server.PingMessageFromServer(),
                    option=orjson.OPT_NAIVE_UTC | orjson.OPT_PASSTHROUGH_DATETIME,
                    default=datetime.isoformat,
                ),
            )

        out_messages = []
        if room.fill_messages(player_id, out_messages):
            for message in out_messages:
                await transmit_bytes(
                    ws,
                    orjson.dumps(
                        message,
                        option=orjson.OPT_NAIVE_UTC | orjson.OPT_PASSTHROUGH_DATETIME,
                        default=datetime.isoformat,
                    ),
                )


async def receive_agent_updates(request, ws, lobby):
    logger.info(f"receive_agent_updates({request}, {ws}, {lobby})")
    GlobalConfig()
    async for msg in ws:
        remote = GetRemote(ws)
        if ws.closed:
            return
        if msg.type == aiohttp.WSMsgType.ERROR:
            await ws.close()
            logger.error("ws connection closed with exception %s" % ws.exception())
            continue

        if msg.type != aiohttp.WSMsgType.TEXT:
            continue

        remote.last_message_up = time.time()
        remote.bytes_up += len(msg.data)

        if msg.data == "close":
            await ws.close()
            continue

        logger.debug("Raw message: " + msg.data)
        message = message_to_server.MessageToServer.from_json(msg.data)

        if message.type == message_to_server.MessageType.GOOGLE_AUTH:
            await google_authenticator.handle_auth(ws, message.google_auth)
            continue

        if message.type == message_to_server.MessageType.USER_INFO:
            await user_info_fetcher.handle_userinfo_request(ws, remote)
            continue

        if message.type == message_to_server.MessageType.ROOM_MANAGEMENT:
            lobby.handle_request(message, ws)
            continue

        if message.type == message_to_server.MessageType.CLIENT_EXCEPTION:
            logger.info(
                f"========== @@@@@@@@@ ############ $$$$$$$$$$$ Client exception: {message.client_exception.condition}"
            )
            client_exception_logger.queue_exception(message.client_exception)
            continue

        if message.type == message_to_server.MessageType.PONG:
            # Calculate the time offset.
            t0 = remote.last_ping.replace(tzinfo=timezone.utc)
            t1 = parser.isoparse(message.pong.ping_receive_time).replace(
                tzinfo=timezone.utc
            )
            t2 = message.transmit_time.replace(tzinfo=timezone.utc)
            t3 = datetime.utcnow().replace(tzinfo=timezone.utc)
            # Calculate clock offset and latency.
            remote.time_offset = (
                (t1 - t0).total_seconds() + (t2 - t3).total_seconds()
            ) / 2
            remote.latency = ((t3 - t0).total_seconds() - (t2 - t1).total_seconds()) / 2
            continue

        if lobby.socket_in_room(ws):
            # Only handle in-game actions if we're in a room.
            (room_id, player_id, _) = lobby.socket_info(ws).as_tuple()
            room = lobby.get_room(room_id)
            room.drain_messages(player_id, [message])
        else:
            # Room manager handles out-of-game requests.
            lobby.handle_request(message, ws)


@routes.get("/player_endpoint")
async def PlayerEndpoint(request):
    if "lobby_name" in request.query:
        lobby = GetLobby(request.query["lobby_name"])
        if lobby == None:
            return web.Response(status=404, text="Lobby not found.")
    else:
        lobby = GetLobby(DEFAULT_LOBBY)
    logger.info(
        f"Player connecting to lobby: {lobby.lobby_name()} | type: {lobby.lobby_type()}"
    )
    assignment = None
    is_mturk = False
    is_bot = False
    if "is_bot" in request.query:
        is_bot = request.query["is_bot"] == "true"
    if "assignmentId" in request.query:
        # If this is an mturk task, log assignment into to the remote table.
        is_mturk = True
        assignment_id = request.query.getone("assignmentId", "")
        hit_id = request.query.getone("hitId", "")
        submit_to_url = request.query.getone("turkSubmitTo", "")
        worker_id = request.query.getone("workerId", "")
        worker, _ = schemas.mturk.Worker.get_or_create(
            hashed_id=hashlib.md5(
                worker_id.encode("utf-8")
            ).hexdigest(),  # Worker ID is PII, so only save the hash.
        )
        assignment, _ = schemas.mturk.Assignment.get_or_create(
            assignment_id=assignment_id,
            worker=worker,
            hit_id=hit_id,
            submit_to_url=submit_to_url,
        )

    ws = web.WebSocketResponse(
        autoclose=True, heartbeat=HEARTBEAT_TIMEOUT_S, autoping=True
    )
    await ws.prepare(request)
    logger.info("player connected from : " + request.remote)
    hashed_ip = "UNKNOWN"
    peername = request.transport.get_extra_info("peername")
    port = 0
    if peername is not None:
        ip = peername[0]
        port = peername[1]
        hashed_ip = hashlib.md5(ip.encode("utf-8")).hexdigest()
    remote = Remote(hashed_ip, port, 0, 0, time.time(), time.time(), request, ws)
    remote = dataclasses.replace(remote, user_type=UserType.OPEN)

    if is_bot:
        remote = dataclasses.replace(remote, user_type=UserType.BOT)

    if is_mturk:
        remote = dataclasses.replace(
            remote, mturk_id=worker_id, user_type=UserType.MTURK
        )

    AddRemote(ws, remote, assignment)
    logger.info(f"Player connected. Type: {repr(remote.user_type)}")
    LogConnectionEvent(remote, "Connected to Server.")
    try:
        await asyncio.gather(
            receive_agent_updates(request, ws, lobby),
            stream_game_state(request, ws, lobby),
        )
    finally:
        logger.info("=====================================")
        logger.info("player disconnected from : " + request.remote)
        LogConnectionEvent(remote, "Disconnected from Server.")
        lobby.disconnect_socket(ws)
        DeleteRemote(ws)
    return ws


def HashCollectAssets(assets_directory):
    assets_map = {}
    assets_directory.mkdir(parents=False, exist_ok=True)
    for item in os.listdir(assets_directory):
        assets_map[hashlib.md5(item.encode()).hexdigest()] = os.path.join(
            assets_directory, item
        )
    return assets_map


# A dictionary from md5sum to asset filename.
assets_map = {}

# Serves assets obfuscated by md5suming the filename.
# This is used to prevent asset discovery.


@routes.get("/assets/{asset_id}")
async def asset(request):
    asset_id = request.match_info.get("asset_id", "")
    if asset_id not in assets_map:
        raise aiohttp.web.HTTPNotFound("/redirect")
    return web.FileResponse(assets_map[asset_id])


async def serve(config):
    # Check if the server/www/WebGL directory exists.
    if not os.path.isdir(os.path.join(PackageRoot() / "server/www/WebGL")):
        logger.warning(
            "WebGL directory not found. This directory contains the compiled Unity front-end. You can download it by running `python3 -m cb2game.server.fetch_client` or manually here https://github.com/lil-lab/cb2/releases. You can also compile from source, but this requires installing Unity and getting a license. See game/ for client code and build_client.sh for instructions building the client from headless mode in Unity."
        )
        return

    # Add a route for serving web frontend files on /.
    routes.static("/", os.path.join(PackageRoot() / "server/www/WebGL"))

    app = web.Application()
    fernet_key = cryptography.fernet.Fernet.generate_key()
    fernet = cryptography.fernet.Fernet(fernet_key)
    setup(
        app,
        EncryptedCookieStorage(fernet, secure=True, httponly=True, samesite="Strict"),
    )
    app.add_routes(routes)
    runner = aiohttp.web.AppRunner(app, handle_signals=True)
    await runner.setup()
    site = web.TCPSite(runner, None, config.http_port)
    await site.start()

    print("======= Serving on {site.name} ======".format(site=site))

    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    while True:
        await asyncio.sleep(1)


def InitPythonLogging():
    """Server logging intended for debugging a server crash.

    The server log includes the following, interlaced:
    - Events from each game room.
    - HTTP connection, error & debug information from aiohttp.
    - Misc other server logs (calls to logger.info()).
    - Exception stack traces."""
    log_format = "[%(asctime)s] %(name)s %(levelname)s [%(module)s:%(funcName)s:%(lineno)d] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("peewee").setLevel(logging.INFO)
    # Disable pdoc warnings.
    warnings.filterwarnings("ignore", module="pdoc")
    logging.getLogger("pdoc").setLevel(logging.INFO)


def InitGameRecording(config):
    """Game recording allows us to record and later playback individual games.

    Games are saved both in a directory with easily human-readable images and in
    an sqlite3 database.

    Each game is given a game id. Logs for a single game are stored in a
    directory with a name of the form:

    game_records/<lobby_name>/<datetime>_<game_id>_<game_type>/...

    where <datetime> is in iso8601 format.
    <game_id> can be used to lookup the game in the database.
    <game_type> is GAME or TUTORIAL.
    <lobby_name> is the name of the lobby that the game was in.
    """
    for lobby in GetLobbies():
        if lobby.lobby_name() == "":
            logger.warning(f"Skipping game recording for lobby with empty name.")
            continue
        record_base_dir = pathlib.Path(config.record_directory()) / lobby.lobby_name()
        # Create the directory if it doesn't exist.
        record_base_dir.mkdir(parents=True, exist_ok=True)
        # Register the logging directory with the room manager.
        lobby.register_game_logging_directory(record_base_dir)

    # Setup the sqlite database used to record game actions.
    base.SetDatabase(config)
    base.ConnectDatabase()
    base.CreateTablesIfNotExists(defaults.ListDefaultTables())


def CreateDataDirectory(config):
    data_prefix = pathlib.Path(config.data_prefix).expanduser()
    # Create the directory if it doesn't exist.
    data_prefix.mkdir(parents=False, exist_ok=True)


def CreateExceptionDirectory(config):
    # A directory to store exception logs. One file per exception.
    exception_dir = config.exception_directory()
    exception_dir.mkdir(parents=False, exist_ok=True)


def main(config_filepath=""):
    global assets_map
    global lobby

    # On exit, deletes temporary download files.
    atexit.register(CleanupDownloadFiles)
    atexit.register(SaveClientExceptionsToDB)

    # If the config filepath doesn't exist, log an error and tell the user to
    # try running `python3 -m cb2game.server.generate_config`.
    if not os.path.isfile(config_filepath):
        logger.error(
            f"Config file not found at {config_filepath}. Try running `python3 -m cb2game.server.generate_config`."
        )
        return

    InitPythonLogging()
    InitGlobalConfig(config_filepath)

    logger.info("Config file parsed.")
    logger.info(f"data prefix: {GlobalConfig().data_prefix}")
    logger.info(f"Log directory: {GlobalConfig().record_directory()}")
    logger.info(f"Assets directory: {GlobalConfig().assets_directory()}")
    logger.info(f"Database path: {GlobalConfig().database_path()}")

    InitializeLobbies(GlobalConfig().lobbies)
    CreateDataDirectory(GlobalConfig())
    CreateExceptionDirectory(GlobalConfig())
    InitGameRecording(GlobalConfig())
    client_exception_logger.set_config(GlobalConfig())

    lobbies = GetLobbies()
    lobby_coroutines = []
    for lobby in lobbies:
        lobby_coroutines.append(lobby.matchmake())
        lobby_coroutines.append(lobby.cleanup_rooms())

    assets_map = HashCollectAssets(GlobalConfig().assets_directory())
    tasks = asyncio.gather(
        *lobby_coroutines,
        serve(GlobalConfig()),
        MapGenerationTask(lobbies, GlobalConfig()),
        DataDownloader(lobbies),
        ExceptionSaver(lobbies, GlobalConfig()),
    )
    loop = asyncio.get_event_loop()
    # loop.set_debug(enabled=True)
    try:
        loop.run_until_complete(tasks)
    except KeyboardInterrupt:
        logger.info(f"Keyboard interrupt received. Exiting.")
        sys.exit(0)
    finally:
        lobby.end_server()
        loop.close()


if __name__ == "__main__":
    fire.Fire(main)
