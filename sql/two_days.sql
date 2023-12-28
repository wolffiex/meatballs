SELECT row_to_json(t)
FROM (
    SELECT
        time_bucket('10 minutes', time) AS time_bucket,
        first(pressure, time) AS pressure,
        first(outdoor_temp, time) AS outdoor_temp
    FROM weather
    GROUP BY time_bucket
    ORDER BY time_bucket DESC
    LIMIT 500
) t;
