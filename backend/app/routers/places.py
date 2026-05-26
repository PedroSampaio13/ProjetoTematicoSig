import json
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.db import SessionLocal

router = APIRouter(prefix="/places", tags=["places"])

WALKING_METERS_PER_MINUTE = 83
WALKING_ROUTE_URL = "https://routing.openstreetmap.de/routed-foot/route/v1/foot"
PLACES_PER_MAJOR_CITY = 3
MAJOR_PORTUGAL_CITIES = (
    {"name": "Lisboa", "lat": 38.7223, "lon": -9.1393},
    {"name": "Porto", "lat": 41.1579, "lon": -8.6291},
    {"name": "Braga", "lat": 41.5454, "lon": -8.4265},
    {"name": "Coimbra", "lat": 40.2033, "lon": -8.4103},
    {"name": "Aveiro", "lat": 40.6405, "lon": -8.6538},
    {"name": "Leiria", "lat": 39.7436, "lon": -8.8071},
    {"name": "Setubal", "lat": 38.5244, "lon": -8.8882},
    {"name": "Evora", "lat": 38.5714, "lon": -7.9135},
    {"name": "Faro", "lat": 37.0194, "lon": -7.9304},
    {"name": "Funchal", "lat": 32.6669, "lon": -16.9241},
)
CATEGORY_ALIASES = {
    "farmacias": "farmacia",
    "hospitais": "hospital",
    "restaurantes": "restaurante",
}


class PlaceSearchRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    max_travel_time: int = Field(15, gt=0, le=120)
    categorias: list[str] = Field(default_factory=list)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/categorias")
def get_categorias(db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT id, name FROM category ORDER BY name")).fetchall()
    return [{"id": row[0], "name": row[1]} for row in rows]


def build_category_filter(sql: str, params: dict, categorias: list[str]):
    if not categorias:
        return sql

    placeholders = []
    for index, categoria in enumerate(categorias):
        key = f"categoria_{index}"
        placeholders.append(f":{key}")
        params[key] = categoria

    return sql + f" AND cat.name IN ({', '.join(placeholders)})"


def normalize_category(categoria: Optional[str]):
    if not categoria:
        return None

    normalized = unicodedata.normalize("NFKD", categoria.strip().lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return CATEGORY_ALIASES.get(normalized, normalized)


def format_places(rows):
    return [
        {
            "id": row[0],
            "nome": row[1],
            "morada": row[2],
            "lat": float(row[3]),
            "lon": float(row[4]),
            "categoria": row[5],
            "distancia_m": round(float(row[6])),
            "tempo_min": max(1, round(float(row[6]) / WALKING_METERS_PER_MINUTE)),
        }
        for row in rows
    ]


def format_places_without_distance(rows):
    return [
        {
            "id": row[0],
            "nome": row[1],
            "morada": row[2],
            "lat": float(row[3]),
            "lon": float(row[4]),
            "categoria": row[5],
        }
        for row in rows
    ]


def calculate_walking_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float):
    url = (
        f"{WALKING_ROUTE_URL}/"
        f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        "?overview=false&geometries=geojson&steps=false"
    )

    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None

    routes = data.get("routes", [])
    if not routes:
        return None

    route = routes[0]
    return {
        "distance_m": round(route["distance"]),
        "duration_min": max(1, round(route["duration"] / 60)),
    }


def format_places_with_walking_routes(rows, origin_lat: float, origin_lon: float, max_travel_time: int):
    routed_places = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        route_jobs = {
            executor.submit(
                calculate_walking_route,
                origin_lat,
                origin_lon,
                float(row[3]),
                float(row[4]),
            ): row
            for row in rows
        }

        for job in as_completed(route_jobs):
            row = route_jobs[job]
            try:
                route = job.result()
            except Exception:
                route = None
            if not route or route["duration_min"] > max_travel_time:
                continue

            routed_places.append(
                {
                    "id": row[0],
                    "nome": row[1],
                    "morada": row[2],
                    "lat": float(row[3]),
                    "lon": float(row[4]),
                    "categoria": row[5],
                    "distancia_m": route["distance_m"],
                    "tempo_min": route["duration_min"],
                }
            )

    return sorted(routed_places, key=lambda place: (place["tempo_min"], place["distancia_m"]))[:50]


def find_places_within_radius(
    db: Session,
    lat: float,
    lon: float,
    radius_m: int,
    categorias: list[str],
):
    sql = """
        SELECT
            poi.id,
            poi.name,
            poi.address,
            poi.latitude,
            poi.longitude,
            cat.name,
            ST_Distance(
                poi.geometry::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) AS distance_m
        FROM point_of_interest poi
        JOIN category cat ON poi.category_id = cat.id
        WHERE ST_DWithin(
            poi.geometry::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            :radius_m
        )
    """
    params = {"lat": lat, "lon": lon, "radius_m": radius_m}
    sql = build_category_filter(sql, params, categorias)
    sql += " ORDER BY distance_m ASC LIMIT 50"

    return db.execute(text(sql), params).fetchall()


def find_places_near_major_cities(
    db: Session,
    categoria: str,
    places_per_city: int = PLACES_PER_MAJOR_CITY,
):
    city_rows = []
    params = {"categoria": categoria, "places_per_city": places_per_city}

    for index, city in enumerate(MAJOR_PORTUGAL_CITIES):
        city_rows.append(
            f"(:city_{index}_name, :city_{index}_lat, :city_{index}_lon, :city_{index}_sort)"
        )
        params[f"city_{index}_name"] = city["name"]
        params[f"city_{index}_lat"] = city["lat"]
        params[f"city_{index}_lon"] = city["lon"]
        params[f"city_{index}_sort"] = index

    sql = f"""
        WITH cities(name, lat, lon, sort_order) AS (
            VALUES {", ".join(city_rows)}
        )
        SELECT
            city_places.id,
            city_places.name,
            city_places.address,
            city_places.latitude,
            city_places.longitude,
            city_places.category_name
        FROM cities
        CROSS JOIN LATERAL (
            SELECT
                poi.id,
                poi.name,
                poi.address,
                poi.latitude,
                poi.longitude,
                cat.name AS category_name,
                ST_Distance(
                    poi.geometry::geography,
                    ST_SetSRID(ST_MakePoint(cities.lon, cities.lat), 4326)::geography
                ) AS distance_m
            FROM point_of_interest poi
            JOIN category cat ON poi.category_id = cat.id
            WHERE cat.name = :categoria
            ORDER BY poi.geometry <-> ST_SetSRID(ST_MakePoint(cities.lon, cities.lat), 4326)
            LIMIT :places_per_city
        ) city_places
        ORDER BY cities.sort_order, city_places.distance_m ASC
    """

    return db.execute(text(sql), params).fetchall()


@router.post("/search")
def create_place_search(
    payload: PlaceSearchRequest,
    db: Session = Depends(get_db),
):
    radius_m = payload.max_travel_time * WALKING_METERS_PER_MINUTE
    categorias = payload.categorias

    try:
        location_id = db.execute(
            text("""
                INSERT INTO location (latitude, longitude, geometry)
                VALUES (
                    :lat,
                    :lon,
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                )
                RETURNING id
            """),
            {"lat": payload.lat, "lon": payload.lon},
        ).scalar_one()

        search_request_id = db.execute(
            text("""
                INSERT INTO search_request (
                    location_id,
                    max_travel_time,
                    requested_categories
                )
                VALUES (
                    :location_id,
                    :max_travel_time,
                    CAST(:requested_categories AS jsonb)
                )
                RETURNING id
            """),
            {
                "location_id": location_id,
                "max_travel_time": payload.max_travel_time,
                "requested_categories": json.dumps(categorias),
            },
        ).scalar_one()

        route_area_geojson = db.execute(
            text("""
                INSERT INTO route_area (search_request_id, geometry)
                VALUES (
                    :search_request_id,
                    ST_Buffer(
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                        :radius_m
                    )::geometry
                )
                RETURNING ST_AsGeoJSON(geometry)
            """),
            {
                "search_request_id": search_request_id,
                "lat": payload.lat,
                "lon": payload.lon,
                "radius_m": radius_m,
            },
        ).scalar_one()

        candidate_rows = find_places_within_radius(
            db=db,
            lat=payload.lat,
            lon=payload.lon,
            radius_m=radius_m,
            categorias=categorias,
        )
        routed_places = format_places_with_walking_routes(
            candidate_rows,
            payload.lat,
            payload.lon,
            payload.max_travel_time,
        )

        for place in routed_places:
            db.execute(
                text("""
                    INSERT INTO map_result (
                        search_request_id,
                        poi_id,
                        estimated_time
                    )
                    VALUES (
                        :search_request_id,
                        :poi_id,
                        :estimated_time
                    )
                """),
                {
                    "search_request_id": search_request_id,
                    "poi_id": place["id"],
                    "estimated_time": place["tempo_min"],
                },
            )

        db.commit()

        return {
            "search_request_id": search_request_id,
            "location_id": location_id,
            "route_area": json.loads(route_area_geojson),
            "results": routed_places,
        }
    except Exception:
        db.rollback()
        raise


@router.get("/nearby")
def get_nearby_places(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(1250, gt=0, le=10000),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    normalized_categoria = normalize_category(categoria)
    categorias = [normalized_categoria] if normalized_categoria else []
    rows = find_places_within_radius(db, lat, lon, radius_m, categorias)
    return format_places(rows)


@router.get("/")
def get_places(
    query: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    normalized_categoria = normalize_category(categoria)

    if normalized_categoria and not query:
        rows = find_places_near_major_cities(db, normalized_categoria)
        return format_places_without_distance(rows)

    sql = """
        SELECT poi.id, poi.name, poi.address, poi.latitude, poi.longitude, cat.name
        FROM point_of_interest poi
        JOIN category cat ON poi.category_id = cat.id
        WHERE 1=1
    """
    params: dict = {}

    if query:
        sql += " AND unaccent(poi.name) ILIKE unaccent(:query)"
        params["query"] = f"%{query}%"

    if normalized_categoria:
        sql += " AND cat.name = :categoria"
        params["categoria"] = normalized_categoria

    sql += " LIMIT 50"

    rows = db.execute(text(sql), params).fetchall()
    return format_places_without_distance(rows)
