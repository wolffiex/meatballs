import asyncio
import json
from time import sleep
import psycopg

PRESSURE_SELECT = """SELECT
    EXTRACT(EPOCH FROM time_bucket('10 minutes', time)) AS bucket_epoch,
    first(pressure,time)
    FROM weather
    GROUP BY bucket_epoch 
    ORDER BY bucket_epoch
    LIMIT 500;
"""


async def gen_barometer_chart(q, aconn):
    async with aconn.cursor() as cur:
        await cur.execute(PRESSURE_SELECT)

        async for record in cur:  # Iterate directly over the cursor
            bucket, pressure = record
            await q.put(["barometer", int(bucket), float(pressure)])

        await q.put(["barometer", "STOP"])


async def gen_pressure(q, id):
    await q.put([id, "x", {"foo": "far"}])
    await asyncio.sleep(1)
    await q.put([id, "y", {"boo": "bar"}])
    await asyncio.sleep(1)
    await q.put([id, "z", {"boo": "bar"}])
    await asyncio.sleep(1)
    await q.put([id, "zz", {"boo": "bar"}])
    await asyncio.sleep(1)
    await q.put([id, "zzz", {"boo": "bar"}])


def output(item):
    print(f"data: {json.dumps(item)}\n\n", flush=True)


async def gather(q, producers):
    await asyncio.gather(*producers)
    await q.put("STOP")


async def main():
    db_args = {
        "dbname": "monitoring",
        "user": "adam",
        "password": "adam",
        "host": "haus.local",
    }
    async with await psycopg.AsyncConnection.connect(**db_args) as aconn:
        q = asyncio.Queue()
        # List of async methods to run in the background
        producers = [gen_pressure(q, "a"), gen_barometer_chart(q, aconn)]
        background_task = asyncio.create_task(gather(q, producers))
        while True:
            item = await q.get()
            output(item)
            if item == "STOP":
                break
        await background_task


asyncio.run(main())


# def gen_events():
#     yield from gen_barometer_chart(conn)
