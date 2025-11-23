"""
Failed Searches Router - API Endpoints für Failed Searches Management
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any

from models import FailedSearch
from services import FailedSearchService

router = APIRouter()


@router.get("/", response_model=List[FailedSearch])
async def get_failed_searches(
    json_file: Optional[str] = Query(None, description="Filter nach JSON-Datei")
):
    """
    Gibt alle Failed Searches zurück
    """
    return FailedSearchService.get_all_failed_searches(json_file)


@router.delete("/{json_file}/{card_id}")
async def delete_failed_search(json_file: str, card_id: str) -> Dict[str, str]:
    """
    Löscht einen Failed Search Eintrag
    """
    return FailedSearchService.delete_failed_search(json_file, card_id)


@router.delete("/{json_file}")
async def delete_all_failed_searches(json_file: str) -> Dict[str, Any]:
    """
    Löscht alle Failed Searches für eine Datei
    """
    return FailedSearchService.delete_all_failed_searches(json_file)


@router.post("/retry")
async def retry_failed_searches(json_file: str, service: str):
    """
    Startet Retry für Failed Searches (Trigger für Import-Script)
    """
    # TODO: Import-Script Integration
    return {
        "message": "Retry wird gestartet",
        "json_file": json_file,
        "service": service
    }
