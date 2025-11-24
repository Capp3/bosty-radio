"""Station database loader and query functions."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Station(BaseModel):
    """Model for a radio station."""

    name: str
    url: str
    category: str


def _get_stations_file_path() -> Path:
    """Get the path to the stations.json file."""
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    return module_dir / "data" / "stations.json"


def load_stations() -> List[Station]:
    """
    Load all stations from the database.

    Returns:
        List of Station objects. Returns empty list if file cannot be loaded.
    """
    stations_path = _get_stations_file_path()

    try:
        with open(stations_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        stations = [Station(**station_data) for station_data in data]
        logger.info(f"Loaded {len(stations)} stations from database")
        return stations

    except FileNotFoundError:
        logger.warning(f"Stations file not found at {stations_path}")
        return []
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error loading stations: {e}")
        return []


def get_stations_by_category() -> Dict[str, List[Station]]:
    """
    Get all stations grouped by category.

    Returns:
        Dictionary mapping category names to lists of Station objects.
    """
    stations = load_stations()
    by_category: Dict[str, List[Station]] = {}

    for station in stations:
        if station.category not in by_category:
            by_category[station.category] = []
        by_category[station.category].append(station)

    return by_category


def get_all_stations() -> List[Station]:
    """
    Get all stations as a flat list.

    This is an alias for load_stations() for consistency with the API.

    Returns:
        List of Station objects.
    """
    return load_stations()


def get_station_by_name(name: str) -> Optional[Station]:
    """
    Find a station by its exact name.

    Args:
        name: The exact station name to search for.

    Returns:
        Station object if found, None otherwise.
    """
    stations = load_stations()
    for station in stations:
        if station.name == name:
            return station
    return None


def search_stations(query: str) -> List[Station]:
    """
    Search for stations by name (case-insensitive substring match).

    Args:
        query: Search query string.

    Returns:
        List of matching Station objects.
    """
    stations = load_stations()
    query_lower = query.lower()
    return [s for s in stations if query_lower in s.name.lower()]
