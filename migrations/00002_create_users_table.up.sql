CREATE TABLE IF NOT EXISTS dwh.users (
    id SERIAL NOT NULL,
    username TEXT,
    phone TEXT,
    "point" GEOGRAPHY(POINT, 4326)
);

-- TODO: do the constrain magic here