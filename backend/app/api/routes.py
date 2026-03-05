"""Central router that includes every sub-router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api import (
    admin,
    alliances,
    auth,
    bootstrap,
    chat,
    club,
    finances,
    friends,
    ladder,
    league,
    lineup,
    scouting,
    shop,
    squad,
    stadium,
    tasks,
    training,
    transfer,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(bootstrap.router)
api_router.include_router(club.router)
api_router.include_router(squad.router)
api_router.include_router(lineup.router)
api_router.include_router(training.router)
api_router.include_router(scouting.router)
api_router.include_router(transfer.router)
api_router.include_router(league.router)
api_router.include_router(ladder.router)
api_router.include_router(friends.router)
api_router.include_router(chat.router)
api_router.include_router(shop.router)
api_router.include_router(stadium.router)
api_router.include_router(finances.router)
api_router.include_router(alliances.router)
api_router.include_router(tasks.router)
api_router.include_router(admin.router)
