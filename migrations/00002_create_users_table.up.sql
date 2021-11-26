CREATE TABLE IF NOT EXISTS dwh.users (
    id SERIAL NOT NULL,
    username TEXT UNIQUE,
    phone TEXT,
    "point" GEOGRAPHY(POINT, 4326)
);