"""
Statistics Router - Dashboard und Statistiken
Nutzt Node.js Cards API
"""

from fastapi import APIRouter
from typing import Dict, Any

from clients.cards_api_client import cards_api_client
from services import FailedSearchService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats() -> Dict[str, Any]:
    """
    Gibt Dashboard-Statistiken zurück
    Nutzt Node.js API für Card-Daten
    """
    # Daten von Node.js API holen
    data = await cards_api_client.get_all_data()
    cards = data.get('cards', [])
    editions = data.get('editions', [])
    
    # Failed Searches von lokalen Dateien
    all_failed = FailedSearchService.get_all_failed_searches()
    
    # Streaming Coverage berechnen
    spotify_count = sum(1 for card in cards if card.get('spotify', {}).get('id'))
    apple_count = sum(1 for card in cards if card.get('apple', {}).get('id'))
    both_count = sum(
        1 for card in cards 
        if card.get('spotify', {}).get('id') and card.get('apple', {}).get('id')
    )
    
    # Neither: Cards ohne Spotify UND ohne Apple
    cards_with_streaming = set()
    for i, card in enumerate(cards):
        if card.get('spotify', {}).get('id') or card.get('apple', {}).get('id'):
            cards_with_streaming.add(i)
    neither_count = len(cards) - len(cards_with_streaming)
    
    total_cards = len(cards)
    
    # Edition Stats
    edition_stats = []
    for edition_info in editions:
        edition_name = edition_info.get('edition')
        json_file = edition_info.get('file')
        
        edition_cards = [c for c in cards if c.get('source_file') == json_file]
        spotify_coverage = sum(1 for c in edition_cards if c.get('spotify', {}).get('id'))
        apple_coverage = sum(1 for c in edition_cards if c.get('apple', {}).get('id'))
        
        failed_for_edition = [
            fs for fs in all_failed
            if fs.json_file == json_file
        ]
        
        edition_stats.append({
            "edition": edition_name,
            "card_count": len(edition_cards),
            "spotify_coverage": spotify_coverage,
            "apple_coverage": apple_coverage,
            "failed_searches": len(failed_for_edition)
        })
    
    return {
        "total_cards": total_cards,
        "total_editions": len(editions),
        "total_failed_searches": len(all_failed),
        "streaming_coverage": {
            "spotify_count": spotify_count,
            "apple_count": apple_count,
            "both_count": both_count,
            "neither_count": neither_count,
            "spotify_percentage": round(spotify_count / total_cards * 100, 2) if total_cards > 0 else 0,
            "apple_percentage": round(apple_count / total_cards * 100, 2) if total_cards > 0 else 0,
            "both_percentage": round(both_count / total_cards * 100, 2) if total_cards > 0 else 0,
        },
        "edition_stats": edition_stats,
        "recent_failed_searches": [
            {
                "card_id": fs.card_id,
                "artist": fs.artist,
                "title": fs.title,
                "year": fs.year,
                "json_file": fs.json_file,
                "timestamp": fs.timestamp
            }
            for fs in all_failed[:10]
        ]
    }


@router.get("/coverage")
async def get_coverage_stats() -> Dict[str, Any]:
    """
    Gibt detaillierte Coverage-Statistiken zurück
    """
    data = await cards_api_client.get_all_data()
    cards = data.get('cards', [])
    
    # Coverage nach Jahr
    year_coverage = {}
    for card in cards:
        year = card.get('year', 'Unknown')
        if year not in year_coverage:
            year_coverage[year] = {
                'total': 0,
                'spotify': 0,
                'apple': 0,
                'both': 0
            }
        
        year_coverage[year]['total'] += 1
        if card.get('spotify', {}).get('id'):
            year_coverage[year]['spotify'] += 1
        if card.get('apple', {}).get('id'):
            year_coverage[year]['apple'] += 1
        if card.get('spotify', {}).get('id') and card.get('apple', {}).get('id'):
            year_coverage[year]['both'] += 1
    
    return {
        "by_year": year_coverage,
        "total_cards": len(cards)
    }


@router.get("/editions")
async def get_editions() -> Dict[str, Any]:
    """
    Gibt Liste aller verfügbaren Editionen zurück
    """
    data = await cards_api_client.get_all_data()
    editions = data.get('editions', [])
    
    return {
        "editions": [
            {
                "name": edition.get('edition'),
                "file": edition.get('file'),
                "card_count": edition.get('card_count', 0)
            }
            for edition in editions
        ]
    }
