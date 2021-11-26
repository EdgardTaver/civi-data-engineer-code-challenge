CREATE TABLE IF NOT EXISTS dwh.markers (
    id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
    created_at timestamptz NULL DEFAULT NOW(),
    updated_at timestamptz NULL DEFAULT NOW(),
    deleted_at timestamptz NULL,
    point GEOGRAPHY(POINT, 4326) NOT NULL
);