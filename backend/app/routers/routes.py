import json
import math
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/routes", tags=["routes"])

WALKING_METERS_PER_MINUTE = 83
ROUTE_REQUEST_TIMEOUT_SECONDS = 4
ROUTE_CACHE_SIZE = 512

ROUTING_PROFILES = {
    "driving": {
        "base_url": "https://routing.openstreetmap.de/routed-car/route/v1",
        "osrm_profile": "car",
    },
    "walking": {
        "base_url": "https://routing.openstreetmap.de/routed-foot/route/v1",
        "osrm_profile": "foot",
    },
    "cycling": {
        "base_url": "https://routing.openstreetmap.de/routed-bike/route/v1",
        "osrm_profile": "bike",
    },
}


class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class RouteRequest(BaseModel):
    origin: Coordinate
    destination: Coordinate
    profile: str = Field("walking", pattern="^(driving|walking|cycling)$")


def haversine_distance_m(origin: Coordinate, destination: Coordinate):
    earth_radius_m = 6371000
    lat1 = math.radians(origin.lat)
    lat2 = math.radians(destination.lat)
    delta_lat = math.radians(destination.lat - origin.lat)
    delta_lon = math.radians(destination.lon - origin.lon)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return earth_radius_m * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def fallback_route(payload: RouteRequest):
    distance_m = round(haversine_distance_m(payload.origin, payload.destination))
    duration_min = max(1, round(distance_m / WALKING_METERS_PER_MINUTE))

    return {
        "distance_m": distance_m,
        "duration_min": duration_min,
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [payload.origin.lon, payload.origin.lat],
                [payload.destination.lon, payload.destination.lat],
            ],
        },
        "profile": payload.profile,
        "estimated": True,
    }


@lru_cache(maxsize=ROUTE_CACHE_SIZE)
def fetch_route(
    base_url: str,
    osrm_profile: str,
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
):
    url = (
        f"{base_url}/"
        f"{osrm_profile}/"
        f"{origin_lon},{origin_lat};"
        f"{destination_lon},{destination_lat}"
        "?overview=full&geometries=geojson&steps=false"
    )

    with urlopen(url, timeout=ROUTE_REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


@router.post("/calculate")
def calculate_route(payload: RouteRequest):
    routing_profile = ROUTING_PROFILES[payload.profile]

    try:
        data = fetch_route(
            routing_profile["base_url"],
            routing_profile["osrm_profile"],
            round(payload.origin.lat, 6),
            round(payload.origin.lon, 6),
            round(payload.destination.lat, 6),
            round(payload.destination.lon, 6),
        )
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return fallback_route(payload)

    routes = data.get("routes", [])
    if not routes:
        return fallback_route(payload)

    route = routes[0]
    return {
        "distance_m": round(route["distance"]),
        "duration_min": max(1, round(route["duration"] / 60)),
        "geometry": route["geometry"],
        "profile": payload.profile,
        "estimated": False,
    }
