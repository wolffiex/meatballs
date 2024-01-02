CREATE TABLE weather (
    time TIMESTAMPTZ NOT NULL,
    indoor_temp NUMERIC,
    pressure NUMERIC,
    outdoor_temp NUMERIC,
    humidity NUMERIC,
    wind_speed NUMERIC,
    solar_radiation NUMERIC,
    uvi NUMERIC,
    rain_rate NUMERIC
);
SELECT create_hypertable('weather', 'time');
