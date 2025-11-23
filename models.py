"""
Pydantic Models für Admin API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Card Models
class SpotifyData(BaseModel):
    id: str = ""
    uri: str = ""


class AppleData(BaseModel):
    id: str = ""
    uri: str = ""


class Card(BaseModel):
    id: str = Field(..., alias="cardId")
    title: str
    artist: str
    year: str
    spotify: Optional[SpotifyData] = None
    apple: Optional[AppleData] = None
    edition: Optional[str] = None
    language_short: Optional[str] = None
    language_long: Optional[str] = None
    source_file: Optional[str] = None
    
    class Config:
        populate_by_name = True


class CardUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[str] = None
    spotify: Optional[SpotifyData] = None
    apple: Optional[AppleData] = None


# Failed Search Models
class FailedSearch(BaseModel):
    json_file: str
    card_id: str
    artist: str
    title: str
    year: str
    reason: str
    search_url: Optional[str] = None
    timestamp: str


class FailedSearchesFile(BaseModel):
    failed_searches: List[FailedSearch]
    updated: str


# File Models
class FileInfo(BaseModel):
    filename: str
    path: str
    size: int
    card_count: Optional[int] = None
    edition: Optional[str] = None
    has_failed_searches: bool = False


class FileStats(BaseModel):
    total_files: int
    total_cards: int
    files: List[FileInfo]


# Statistics Models
class StreamingCoverage(BaseModel):
    spotify_count: int
    apple_count: int
    both_count: int
    neither_count: int
    spotify_percentage: float
    apple_percentage: float
    both_percentage: float


class EditionStats(BaseModel):
    edition: str
    card_count: int
    spotify_coverage: int
    apple_coverage: int
    failed_searches: int


class DashboardStats(BaseModel):
    total_cards: int
    total_editions: int
    total_failed_searches: int
    streaming_coverage: StreamingCoverage
    edition_stats: List[EditionStats]
    recent_failed_searches: List[FailedSearch]


# Import Models
class ImportRequest(BaseModel):
    json_file: str
    service: str  # "spotify" or "apple"
    retry_mode: bool = False


class ImportStatus(BaseModel):
    running: bool
    json_file: Optional[str] = None
    service: Optional[str] = None
    progress: int = 0
    total: int = 0
    status_message: str = ""
    started_at: Optional[datetime] = None


class ImportResult(BaseModel):
    success: bool
    json_file: str
    service: str
    updated_count: int
    failed_count: int
    skipped_count: int
    message: str
