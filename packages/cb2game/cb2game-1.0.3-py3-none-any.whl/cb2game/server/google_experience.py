""" Code for updating the Google user experience table. """
import json
import logging

import peewee

import cb2game.server.schemas.google_user as google_db
from cb2game.server.experience import (
    InitExperience,
    update_follower_stats,
    update_leader_stats,
)
from cb2game.server.lobby_consts import IsGoogleLobby, LobbyType
from cb2game.server.messages.rooms import Role
from cb2game.server.schemas.mturk import WorkerExperience

logger = logging.getLogger()


def GetOrCreateUserExperienceEntry(hashed_user_id):
    user_query = (
        google_db.GoogleUser.select()
        .join(WorkerExperience, join_type=peewee.JOIN.LEFT_OUTER)
        .where(google_db.GoogleUser.hashed_google_id == hashed_user_id)
    )
    if user_query.count() == 0:
        logger.warning(
            f"User {hashed_user_id} does not exist in the database. Skipping."
        )
        return None
    user = user_query.get()
    if user.experience is None:
        user.experience = WorkerExperience.create()
        user.experience.save()
        user.save()
    return user.experience


def GetUserExperienceEntry(hashed_user_id):
    user_query = (
        google_db.GoogleUser.select()
        .join(WorkerExperience, join_type=peewee.JOIN.LEFT_OUTER)
        .where(google_db.GoogleUser.hashed_google_id == hashed_user_id)
    )
    if user_query.count() == 0:
        logger.warning(
            f"User {google_user_id} does not exist in the database. Skipping."
        )
        return None
    user = user_query.get()
    return user.experience


def InitUserExperience(user):
    """Initializes a worker's experience table."""
    user.experience = InitExperience()
    user.save()


def UpdateLeaderExperience(game_record):
    # Update leader lead & total scores.
    if game_record.google_leader is None:
        logger.info(f"No google leader found.")
        return
    leader_experience = GetOrCreateUserExperienceEntry(
        game_record.google_leader.hashed_google_id
    )
    if leader_experience is None:
        logger.info(f"No lexp entry found.")
        return
    print(f"Leader EXP ID: {leader_experience.id}")
    update_leader_stats(leader_experience, game_record)


def UpdateFollowerExperience(game_record):
    # Update follower follow & total scores.
    if game_record.google_follower is None:
        logger.info(f"No google follower found.")
        return
    follower_experience = GetOrCreateUserExperienceEntry(
        game_record.google_follower.hashed_google_id
    )
    if follower_experience is None:
        logger.info(f"No fexp entry found.")
        return
    print(f"Follower EXP ID: {follower_experience.id}")
    update_follower_stats(follower_experience, game_record)


def UpdateGoogleUserExperienceTable(game_record):
    """Given a game record (joined with leader & followers) updates leader & follower experience table."""
    logger.info(f"Updating google experience...")
    game_type_components = game_record.type.split("|")
    if len(game_type_components) < 3:
        logger.info(f"Game type {game_record.type} is not a lobby game type.")
        return
    (lobby_name, lobby_type_string, game_type) = game_type_components
    lobby_type = LobbyType(int(lobby_type_string))
    if not IsGoogleLobby(lobby_type):
        # Only update the leader & follower experience table for google lobbies.
        logger.info(f"Game type {game_record.type} is not a google lobby game type.")
        return
    logger.info(f"Updating leader experience...")
    UpdateLeaderExperience(game_record)
    logger.info(f"Updating follower experience...")
    UpdateFollowerExperience(game_record)


def MarkTutorialCompleted(google_user, role):
    """Marks the tutorial as completed for the given user and role."""
    if google_user is None:
        logger.warning("No google user found. Not marking tutorial as completed.")
        return
    kvals = json.loads(google_user.kv_store)
    if role == Role.LEADER:
        kvals["leader_tutorial"] = True
    elif role == Role.FOLLOWER:
        kvals["follower_tutorial"] = True
    google_user.kv_store = json.dumps(kvals)
    google_user.save()
    return
