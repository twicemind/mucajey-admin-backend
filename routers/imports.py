"""
Imports Router - API Endpoints für Import Tools
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import subprocess
from pathlib import Path

from models import ImportRequest, ImportStatus, ImportResult
from config import settings

router = APIRouter()

# Global Import Status (in production würde man Redis/DB nutzen)
import_status = ImportStatus(running=False)


async def run_import_script(json_file: str, service: str, retry_mode: bool):
    """
    Führt das Import-Script als Background-Task aus
    """
    global import_status
    
    import_status.running = True
    import_status.json_file = json_file
    import_status.service = service
    import_status.status_message = "Import wird gestartet..."
    
    try:
        if service == "spotify":
            script_name = "update-spotify-ids.py"
        elif service == "apple":
            script_name = "update-apple-music-ids-v2.py"
        else:
            raise ValueError(f"Unbekannter Service: {service}")
        
        script_path = settings.SCRIPTS_DIR / script_name
        
        # Command zusammenbauen
        cmd = ["python", str(script_path), json_file]
        if retry_mode:
            cmd.append("--retry")
        
        import_status.status_message = f"Führe {script_name} aus..."
        
        # Script ausführen
        result = subprocess.run(
            cmd,
            cwd=str(settings.SCRIPTS_DIR),
            capture_output=True,
            text=True,
            timeout=3600  # 1 Stunde Timeout
        )
        
        if result.returncode == 0:
            import_status.status_message = "Import erfolgreich abgeschlossen"
        else:
            import_status.status_message = f"Import fehlgeschlagen: {result.stderr}"
        
    except Exception as e:
        import_status.status_message = f"Fehler beim Import: {str(e)}"
    finally:
        import_status.running = False


@router.post("/start", response_model=Dict[str, Any])
async def start_import(
    request: ImportRequest,
    background_tasks: BackgroundTasks
):
    """
    Startet einen Import-Prozess im Hintergrund
    """
    if import_status.running:
        raise HTTPException(
            status_code=409,
            detail="Ein Import läuft bereits. Bitte warten Sie bis dieser abgeschlossen ist."
        )
    
    # Prüfe ob Datei existiert
    json_path = settings.DATA_DIR / request.json_file
    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Datei {request.json_file} nicht gefunden"
        )
    
    # Starte Import im Hintergrund
    background_tasks.add_task(
        run_import_script,
        request.json_file,
        request.service,
        request.retry_mode
    )
    
    return {
        "message": "Import wurde gestartet",
        "json_file": request.json_file,
        "service": request.service,
        "retry_mode": request.retry_mode
    }


@router.get("/status", response_model=ImportStatus)
async def get_import_status():
    """
    Gibt den aktuellen Status des Import-Prozesses zurück
    """
    return import_status


@router.post("/cancel")
async def cancel_import():
    """
    Bricht den laufenden Import ab (TODO: Implementation)
    """
    if not import_status.running:
        raise HTTPException(
            status_code=400,
            detail="Kein Import läuft aktuell"
        )
    
    # TODO: Process-Abbruch implementieren
    return {
        "message": "Import-Abbruch angefordert (noch nicht implementiert)",
        "json_file": import_status.json_file
    }
