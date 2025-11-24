"""
HTTP Client für die Node.js Cards API
"""

import httpx
from typing import List, Dict, Any, Optional
from config import settings


class CardsAPIClient:
    """Client für die Node.js Cards API (Port 3000)"""
    
    def __init__(self):
        # Node.js Backend ist im gleichen Docker-Netzwerk als 'mucajey-backend' erreichbar
        # Für lokale Entwicklung: localhost:3000
        self.base_url = settings.CARDS_API_URL
        self.api_key = settings.CARDS_API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_all_data(self) -> Dict[str, Any]:
        """
        Ruft alle Cards aus allen Editionen ab
        GET /api/files/all-data
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/files/all-data",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_files(self) -> Dict[str, List[str]]:
        """
        Ruft Liste aller verfügbaren JSON-Dateien ab
        GET /api/files
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/files",
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_file_data(self, filename: str) -> Dict[str, Any]:
        """
        Ruft Daten einer spezifischen JSON-Datei ab
        GET /api/data/:filename
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/data/{filename}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_card_by_id(self, card_id: str) -> Optional[Dict[str, Any]]:
        """
        Ruft eine Card nach ID ab (nur hitster-de.json)
        GET /api/cards/:id
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/cards/{card_id}",
                headers=self.headers,
                timeout=10.0
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    
    async def update_apple_data(
        self, 
        edition: str, 
        card_id: str, 
        apple_id: str, 
        apple_uri: str
    ) -> Dict[str, Any]:
        """
        Aktualisiert Apple Music Daten einer Card
        PATCH /api/cards/:edition/:cardId/apple
        """
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/cards/{edition}/{card_id}/apple",
                headers=self.headers,
                json={
                    "appleId": apple_id,
                    "appleUri": apple_uri
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def batch_update_apple_data(
        self, 
        updates: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Batch-Update für Apple Music Daten
        PATCH /api/cards/apple/batch
        
        updates: Liste von Dicts mit edition, cardId, appleId, appleUri
        """
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/cards/apple/batch",
                headers=self.headers,
                json={"updates": updates},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
    
    async def create_file(
        self,
        edition: str,
        identifier: str,
        language_short: str = "de",
        language_long: str = "Deutsch"
    ) -> Dict[str, Any]:
        """
        Erstellt eine neue JSON-Datei
        POST /api/files
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/files",
                headers=self.headers,
                json={
                    "edition": edition,
                    "identifier": identifier,
                    "language_short": language_short,
                    "language_long": language_long
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def create_card(
        self,
        filename: str,
        card_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fügt eine neue Card zu einer Edition hinzu
        POST /api/files/:filename/cards
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/files/{filename}/cards",
                headers=self.headers,
                json=card_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def update_card(
        self,
        filename: str,
        card_id: str,
        card_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aktualisiert eine bestehende Card
        PUT /api/files/:filename/cards/:cardId
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api/files/{filename}/cards/{card_id}",
                headers=self.headers,
                json=card_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    
    async def sync_spotify_playlist(
        self,
        filename: str
    ) -> Dict[str, Any]:
        """
        Synchronisiert Spotify-Daten aus der Playlist für ein File
        POST /api/files/:filename/spotify-sync
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/files/{filename}/spotify-sync",
                headers=self.headers,
                timeout=300.0  # 5 Minuten Timeout für große Playlists
            )
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> bool:
        """
        Prüft ob die Node.js API erreichbar ist
        GET /health
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception:
            return False


# Globale Client-Instanz
cards_api_client = CardsAPIClient()
