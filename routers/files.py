"""
Files Router - API Endpoints für File Management
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
import httpx

from models import FileStats
from services import FileService
from clients.cards_api_client import cards_api_client

router = APIRouter()


class CreateFileRequest(BaseModel):
    edition: str
    identifier: str
    language_short: str = "de"
    language_long: str = "Deutsch"


@router.get("/", response_model=FileStats)
async def get_files():
    """
    Gibt alle JSON-Dateien mit Statistiken zurück
    """
    return FileService.get_all_files()


@router.get("/{filename}")
async def get_file_content(filename: str) -> Dict[str, Any]:
    """
    Gibt den Inhalt einer JSON-Datei zurück
    """
    return FileService.get_file_content(filename)


@router.post("/")
async def create_file(request: CreateFileRequest) -> Dict[str, Any]:
    """
    Erstellt eine neue JSON-Datei über die Node.js API
    """
    try:
        # Validiere identifier Format
        if not request.identifier or len(request.identifier) != 8:
            raise HTTPException(
                status_code=400,
                detail="identifier muss genau 8 Zeichen lang sein"
            )
        
        # Rufe Node.js API auf
        result = await cards_api_client.create_file(
            edition=request.edition,
            identifier=request.identifier,
            language_short=request.language_short,
            language_long=request.language_long
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Erstellen der Datei: {str(e)}"
        )


@router.post("/{filename}/spotify-sync")
async def sync_spotify_playlist(filename: str) -> Dict[str, Any]:
    """
    Synchronisiert Spotify-Daten aus der Playlist für ein File
    """
    try:
        result = await cards_api_client.sync_spotify_playlist(filename=filename)
        return result
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Datei nicht gefunden")
        elif e.response.status_code == 400:
            error_detail = e.response.json().get('message', 'Ungültige Anfrage')
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Spotify Sync fehlgeschlagen: {e.response.text}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Spotify Sync: {str(e)}"
        )
