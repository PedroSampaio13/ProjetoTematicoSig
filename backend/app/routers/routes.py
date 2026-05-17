import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/routes", tags=["routes"])

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


@router.post("/calculate")
def calculate_route(payload: RouteRequest):
    routing_profile = ROUTING_PROFILES[payload.profile]
    url = (
        f"{routing_profile['base_url']}/"
        f"{routing_profile['osrm_profile']}/"
        f"{payload.origin.lon},{payload.origin.lat};"
        f"{payload.destination.lon},{payload.destination.lat}"
        "?overview=full&geometries=geojson&steps=false"
    )

    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao calcular rota no OSRM: {exc.code}",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=502,
            detail="Nao foi possivel ligar ao servico de rotas.",
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="O servico de rotas demorou demasiado a responder.",
        ) from exc

    routes = data.get("routes", [])
    if not routes:
        raise HTTPException(status_code=404, detail="Nenhuma rota encontrada.")

    route = routes[0]
    return {
        "distance_m": round(route["distance"]),
        "duration_min": max(1, round(route["duration"] / 60)),
        "geometry": route["geometry"],
        "profile": payload.profile,
    }
