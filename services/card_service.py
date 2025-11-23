"""
Card Service - Geschäftslogik für Card Management
Nutzt die Node.js Cards API statt direkten Dateizugriff
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from clients.cards_api_client import cards_api_client


class CardService:
    """Service für Card-Operationen via Node.js API"""
    
    @staticmethod
    async def get_all_cards(
        search: Optional[str] = None,
        json_file: Optional[str] = None,
        year: Optional[str] = None,
        has_spotify: Optional[bool] = None,
        has_apple: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Gibt alle Cards zurück mit optionalen Filtern
        Nutzt GET /api/all-data von der Node.js API
        """
        try:
            # Alle Daten von Node.js API holen
            data = await cards_api_client.get_all_data()
            cards = data.get('cards', [])
            
            # Filter anwenden
            if search:
                search_lower = search.lower()
                cards = [
                    card for card in cards
                    if search_lower in card.get('title', '').lower()
                    or search_lower in card.get('artist', '').lower()
                ]
            
            if json_file:
                cards = [
                    card for card in cards
                    if card.get('source_file') == json_file
                ]
            
            if year:
                cards = [
                    card for card in cards
                    if card.get('year') == year
                ]
            
            if has_spotify is not None:
                cards = [
                    card for card in cards
                    if bool(card.get('spotify', {}).get('id')) == has_spotify
                ]
            
            if has_apple is not None:
                cards = [
                    card for card in cards
                    if bool(card.get('apple', {}).get('id')) == has_apple
                ]
            
            return cards
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Cards: {str(e)}")
    
    @staticmethod
    async def get_card_by_id(card_id: str, json_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Gibt eine Card nach ID zurück
        """
        try:
            if json_file:
                # Spezifische Datei laden
                data = await cards_api_client.get_file_data(json_file)
                cards = data.get('cards', [])
                for card in cards:
                    if card.get('id') == card_id:
                        card['source_file'] = json_file
                        card['edition'] = data.get('edition', '')
                        return card
                return None
            else:
                # Alle Daten durchsuchen
                data = await cards_api_client.get_all_data()
                cards = data.get('cards', [])
                for card in cards:
                    if card.get('id') == card_id:
                        return card
                return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Card: {str(e)}")
    
    @staticmethod
    async def update_card(
        card_id: str,
        json_file: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aktualisiert eine Card via Node.js API
        PUT /api/files/:filename/cards/:cardId
        """
        try:
            result = await cards_api_client.update_card(
                filename=json_file,
                card_id=card_id,
                card_data=update_data
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Aktualisieren der Card: {str(e)}"
            )
    
    @staticmethod
    async def delete_card(card_id: str, json_file: str) -> Dict[str, str]:
        """
        Löscht eine Card
        Hinweis: Derzeit nicht über Node.js API unterstützt
        """
        raise HTTPException(
            status_code=501,
            detail="Delete-Operation noch nicht implementiert"
        )
    
    @staticmethod
    async def create_card(filename: str, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fügt eine neue Card zu einer Edition hinzu
        Nutzt Node.js API: POST /api/files/:filename/cards
        """
        try:
            result = await cards_api_client.create_card(
                filename=filename,
                card_data=card_data
            )
            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Erstellen der Card: {str(e)}"
            )
