import psycopg
import asyncio

async def stream():
    q = asyncio.Queue()

# async def gen_combine(q):
#     v = True
#     while v is not None:
#         v = await q.get()
#         yield v


#     await asyncio.gather(stream1(pool, q), stream2(pool, q))




async def main():
    db_args = {
        "dbname": "monitoring",
        "user": "adam",
        "password": "adam",
        "host": "haus",
    }
    async with await psycopg.AsyncConnection.connect(**db_args) as aconn:
        async with aconn.cursor() as cur:
            async with cur.copy(f"COPY ({q2}) TO STDOUT") as copy:
                async for row in copy.rows():
                    print(row[0])

q1 = """WITH PressureBuckets AS (
    SELECT
        time_bucket('10 minutes', time) as bucket,
        AVG(pressure) as avg_pressure
    FROM weather
    WHERE time >= NOW() - INTERVAL '2 hours'
    GROUP BY bucket
    ORDER BY bucket DESC
)
SELECT json_build_object(
    'time', time,
    'outdoor_temp', outdoor_temp,
    'humidity', humidity,
    'uvi', uvi,
    'rain_rate', rain_rate
) FROM weather ORDER BY time DESC LIMIT 1
UNION ALL
SELECT json_build_object(
    'pressure_difference', (SELECT avg_pressure FROM PressureBuckets ORDER BY bucket DESC LIMIT 1) - 
        (SELECT avg_pressure FROM PressureBuckets ORDER BY bucket DESC OFFSET 6 LIMIT 1)
) FROM PressureBuckets
LIMIT 1
"""
q1="""WITH PressureBuckets AS (
    SELECT
        time_bucket('10 minutes', time) as bucket,
        AVG(pressure) as avg_pressure
    FROM weather
    WHERE time >= NOW() - INTERVAL '2 hours'
    GROUP BY bucket
)
SELECT json_build_object(
    'time', time,
    'outdoor_temp', outdoor_temp,
    'humidity', humidity,
    'uvi', uvi,
    'rain_rate', rain_rate
) FROM (
    SELECT *
    FROM weather
    ORDER BY time DESC
    LIMIT 1
) AS last_weather_record
UNION ALL
SELECT json_build_object(
    'pressure_difference', 
    (SELECT avg_pressure FROM PressureBuckets ORDER BY bucket DESC LIMIT 1) - 
    (SELECT avg_pressure FROM PressureBuckets ORDER BY bucket DESC OFFSET 6 LIMIT 1)
) FROM (
    SELECT 1
) AS single_record
"""

q2="""SELECT row_to_json(t)
FROM (
    SELECT
        time_bucket('10 minutes', time) AS time_bucket,
        avg(pressure) AS pressure,
        avg(outdoor_temp) AS outdoor_temp
    FROM weather
    GROUP BY time_bucket
    ORDER BY time_bucket DESC
    LIMIT 500
) t
"""

asyncio.run(main())
