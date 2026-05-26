CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE OR REPLACE FUNCTION immutable_unaccent(value TEXT)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT unaccent('unaccent', value)
$$;

CREATE TABLE IF NOT EXISTS category (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS location (
    id BIGSERIAL PRIMARY KEY,
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    geometry geometry(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS point_of_interest (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_id BIGINT NOT NULL,
    address TEXT,
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    geometry geometry(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_poi_category
        FOREIGN KEY (category_id)
        REFERENCES category(id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS search_request (
    id BIGSERIAL PRIMARY KEY,
    location_id BIGINT NOT NULL,
    max_travel_time INTEGER NOT NULL DEFAULT 15,
    requested_categories JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_search_location
        FOREIGN KEY (location_id)
        REFERENCES location(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS route_area (
    id BIGSERIAL PRIMARY KEY,
    search_request_id BIGINT NOT NULL UNIQUE,
    geometry geometry(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_route_area_search
        FOREIGN KEY (search_request_id)
        REFERENCES search_request(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS map_result (
    id BIGSERIAL PRIMARY KEY,
    search_request_id BIGINT NOT NULL,
    poi_id BIGINT NOT NULL,
    estimated_time INTEGER,

    CONSTRAINT fk_map_result_search
        FOREIGN KEY (search_request_id)
        REFERENCES search_request(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_map_result_poi
        FOREIGN KEY (poi_id)
        REFERENCES point_of_interest(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_location_geometry
ON location USING GIST (geometry);

CREATE INDEX IF NOT EXISTS idx_poi_geometry
ON point_of_interest USING GIST (geometry);

CREATE INDEX IF NOT EXISTS idx_poi_geometry_geography
ON point_of_interest USING GIST ((geometry::geography));

CREATE INDEX IF NOT EXISTS idx_route_area_geometry
ON route_area USING GIST (geometry);

CREATE INDEX IF NOT EXISTS idx_poi_category
ON point_of_interest (category_id);

CREATE INDEX IF NOT EXISTS idx_poi_name_unaccent_trgm
ON point_of_interest
USING GIN (lower(immutable_unaccent(name)) gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_search_location
ON search_request (location_id);

CREATE INDEX IF NOT EXISTS idx_map_result_search
ON map_result (search_request_id);

CREATE INDEX IF NOT EXISTS idx_map_result_poi
ON map_result (poi_id);
