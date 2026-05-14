import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.db import SessionLocal

router = APIRouter(prefix="/places", tags=["places"])

WALKING_METERS_PER_MINUTE = 83


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

        rows = find_places_within_radius(
            db=db,
            lat=payload.lat,
            lon=payload.lon,
            radius_m=radius_m,
            categorias=categorias,
        )

        for row in rows:
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
                    "poi_id": row[0],
                    "estimated_time": max(
                        1,
                        round(float(row[6]) / WALKING_METERS_PER_MINUTE),
                    ),
                },
            )

        db.commit()

        return {
            "search_request_id": search_request_id,
            "location_id": location_id,
            "route_area": json.loads(route_area_geojson),
            "results": format_places(rows),
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
    categorias = [categoria] if categoria else []
    rows = find_places_within_radius(db, lat, lon, radius_m, categorias)
    return format_places(rows)


@router.get("/")
def get_places(
    query: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
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

    if categoria:
        sql += " AND cat.name = :categoria"
        params["categoria"] = categoria

    sql += " LIMIT 50"

    rows = db.execute(text(sql), params).fetchall()
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
