CREATE TABLE IF NOT EXISTS dwh.users (
    id SERIAL NOT NULL,
    created_at timestamptz NULL DEFAULT NOW(),
    updated_at timestamptz NULL DEFAULT NOW(),
    deleted_at timestamptz NULL,
    username TEXT UNIQUE NOT NULL,
    phone TEXT NULL,
    "point" GEOGRAPHY(POINT, 4326) NULL,
    region TEXT NULL
);