"""
Failed Search Service - Geschäftslogik für Failed Searches Management
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from config import settings
from models import FailedSearch, FailedSearchesFile


class FailedSearchService:
    """Service für Failed Searches"""
    
    @staticmethod
    def get_failed_searches_file_path(json_file: str) -> Path:
        """Gibt den Pfad zur Failed-Searches-Datei zurück"""
        base_name = json_file.replace('.json', '')
        return settings.SCRIPTS_DIR / f"{base_name}-failed-searches.json"
    
    @staticmethod
    def load_failed_searches(json_file: str) -> FailedSearchesFile:
        """Lädt Failed-Searches für eine spezifische JSON-Datei"""
        file_path = FailedSearchService.get_failed_searches_file_path(json_file)
        
        if not file_path.exists():
            return FailedSearchesFile(
                failed_searches=[],
                updated=""
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return FailedSearchesFile(**data)
    
    @staticmethod
    def save_failed_searches(json_file: str, data: FailedSearchesFile) -> None:
        """Speichert Failed-Searches für eine spezifische JSON-Datei"""
        file_path = FailedSearchService.get_failed_searches_file_path(json_file)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data.model_dump(), f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def get_all_failed_searches(json_file: Optional[str] = None) -> List[FailedSearch]:
        """
        Gibt alle Failed Searches zurück
        Wenn json_file angegeben, nur für diese Datei
        """
        if json_file:
            failed_data = FailedSearchService.load_failed_searches(json_file)
            return failed_data.failed_searches
        
        # Alle Failed-Searches-Dateien durchsuchen
        all_failed = []
        failed_files = list(settings.SCRIPTS_DIR.glob("*-failed-searches.json"))
        
        for file_path in failed_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            failed_searches = data.get('failed_searches', [])
            all_failed.extend([FailedSearch(**fs) for fs in failed_searches])
        
        return all_failed
    
    @staticmethod
    def delete_failed_search(json_file: str, card_id: str) -> Dict[str, str]:
        """
        Löscht einen Failed Search Eintrag
        """
        failed_data = FailedSearchService.load_failed_searches(json_file)
        
        original_length = len(failed_data.failed_searches)
        failed_data.failed_searches = [
            fs for fs in failed_data.failed_searches 
            if fs.card_id != card_id
        ]
        
        if len(failed_data.failed_searches) == original_length:
            raise HTTPException(
                status_code=404, 
                detail=f"Failed Search für Card {card_id} in {json_file} nicht gefunden"
            )
        
        FailedSearchService.save_failed_searches(json_file, failed_data)
        
        return {
            "message": f"Failed Search für Card {card_id} erfolgreich gelöscht",
            "json_file": json_file
        }
    
    @staticmethod
    def delete_all_failed_searches(json_file: str) -> Dict[str, Any]:
        """
        Löscht alle Failed Searches für eine Datei
        """
        file_path = FailedSearchService.get_failed_searches_file_path(json_file)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Keine Failed-Searches-Datei für {json_file} gefunden"
            )
        
        # Lösche die Datei
        file_path.unlink()
        
        return {
            "message": f"Alle Failed Searches für {json_file} wurden gelöscht",
            "json_file": json_file
        }
