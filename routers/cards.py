"""
Cards Router - API Endpoints für Card Management
Nutzt Node.js Cards API via HTTP Client
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from services import CardService

router = APIRouter()


class CreateCardRequest(BaseModel):
    filename: str
    id: str
    title: str
    artist: str
    year: str
    apple: Optional[Dict[str, str]] = None
    spotify: Optional[Dict[str, str]] = None


class UpdateCardRequest(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[str] = None
    apple: Optional[Dict[str, str]] = None
    spotify: Optional[Dict[str, str]] = None


@router.get("/", response_model=List[Dict[str, Any]])
async def get_cards(
    json_file: Optional[str] = Query(None, description="Spezifische JSON-Datei filtern"),
    year: Optional[str] = Query(None, description="Nach Jahr filtern"),
    has_spotify: Optional[bool] = Query(None, description="Nur Cards mit/ohne Spotify"),
    has_apple: Optional[bool] = Query(None, description="Nur Cards mit/ohne Apple Music"),
    search: Optional[str] = Query(None, description="Suche in Title/Artist")
):
    """
    Gibt alle Cards zurück mit optionalen Filtern
    Nutzt Node.js Cards API (Port 3000)
    """
    return await CardService.get_all_cards(
        json_file=json_file,
        year=year,
        has_spotify=has_spotify,
        has_apple=has_apple,
        search=search
    )


@router.get("/{card_id}", response_model=Dict[str, Any])
async def get_card(
    card_id: str,
    json_file: Optional[str] = Query(None, description="Spezifische JSON-Datei")
):
    """
    Gibt eine spezifische Card zurück
    """
    card = await CardService.get_card_by_id(card_id, json_file)
    if not card:
        raise HTTPException(status_code=404, detail=f"Card {card_id} nicht gefunden")
    return card


@router.put("/{card_id}", response_model=Dict[str, Any])
async def update_card(
    card_id: str,
    json_file: str = Query(..., description="Dateiname der Edition"),
    update_data: UpdateCardRequest = None
):
    """
    Aktualisiert eine bestehende Card
    """
    try:
        result = await CardService.update_card(
            card_id=card_id,
            json_file=json_file,
            update_data=update_data.dict(exclude_unset=True)
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Aktualisieren der Card: {str(e)}"
        )


@router.delete("/{card_id}")
async def delete_card(
    card_id: str,
    json_file: str
):
    """
    Löscht eine Card (noch nicht implementiert)
    """
    return await CardService.delete_card(card_id, json_file)


@router.post("/")
async def create_card(request: CreateCardRequest) -> Dict[str, Any]:
    """
    Fügt eine neue Card zu einer Edition hinzu
    """
    try:
        result = await CardService.create_card(
            filename=request.filename,
            card_data={
                "id": request.id,
                "title": request.title,
                "artist": request.artist,
                "year": request.year,
                "apple": request.apple or {"id": "", "uri": ""},
                "spotify": request.spotify or {"id": "", "uri": ""}
            }
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Erstellen der Card: {str(e)}"
        )
