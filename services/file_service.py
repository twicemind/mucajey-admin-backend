"""
File Service - Geschäftslogik für File Management
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from config import settings
from models import FileInfo, FileStats


class FileService:
    """Service für File-Operationen"""
    
    @staticmethod
    def get_all_files() -> FileStats:
        """
        Gibt alle JSON-Dateien mit Statistiken zurück
        """
        json_files = list(settings.DATA_DIR.glob("hitster-*.json"))
        
        # Überspringe Backup-Dateien
        json_files = [
            f for f in json_files 
            if 'backup' not in f.stem and 'import' not in f.stem
        ]
        
        files_info = []
        total_cards = 0
        
        for file_path in json_files:
            # Lade JSON für Statistiken
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            card_count = len(data.get('cards', []))
            total_cards += card_count
            
            # Prüfe ob Failed-Searches-Datei existiert
            base_name = file_path.stem
            failed_searches_file = settings.SCRIPTS_DIR / f"{base_name}-failed-searches.json"
            has_failed_searches = failed_searches_file.exists()
            
            files_info.append(
                FileInfo(
                    filename=file_path.name,
                    path=str(file_path),
                    size=file_path.stat().st_size,
                    card_count=card_count,
                    edition=data.get('edition', ''),
                    has_failed_searches=has_failed_searches
                )
            )
        
        # Sortiere nach Dateiname
        files_info.sort(key=lambda x: x.filename)
        
        return FileStats(
            total_files=len(files_info),
            total_cards=total_cards,
            files=files_info
        )
    
    @staticmethod
    def get_file_content(filename: str) -> Dict[str, Any]:
        """
        Gibt den Inhalt einer JSON-Datei zurück
        """
        file_path = settings.DATA_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Datei {filename} nicht gefunden")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
