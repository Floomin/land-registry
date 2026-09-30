"""Робота з геометрією: WKT (STAsText) -> GeoJSON через shapely."""
import json

from shapely import wkt as shapely_wkt
from shapely.geometry import mapping as shapely_mapping


def wkt_to_geojson(wkt_str: str | None) -> str | None:
    """SQL Server STAsText() -> GeoJSON string (STAsGeoJSON() недоступний на цьому сервері)."""
    if not wkt_str:
        return None
    try:
        return json.dumps(shapely_mapping(shapely_wkt.loads(wkt_str)))
    except Exception:  # noqa: BLE001
        return None


def bounds_of_geojson(geoms: list[dict]) -> list[list[float]] | None:
    lats: list[float] = []
    lons: list[float] = []

    def walk(coords):
        if not coords:
            return
        if isinstance(coords[0], (int, float)):
            lons.append(coords[0])
            lats.append(coords[1])
        else:
            for c in coords:
                walk(c)

    for g in geoms:
        walk(g.get("coordinates", []))
    if not lats:
        return None
    return [[min(lats), min(lons)], [max(lats), max(lons)]]
