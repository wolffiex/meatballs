import asyncio
import json
from typing import Any, Generator
import psycopg

PRESSURE_SELECT = """SELECT
    EXTRACT(EPOCH FROM time_bucket('10 minutes', time)) AS bucket_epoch,
    first(pressure,time)
    FROM weather
    GROUP BY bucket_epoch 
    ORDER BY bucket_epoch
    LIMIT 50;
"""


class TaskMan:
    def __init__(self):
        self.tasks = []
        self.task_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        self.background_task = asyncio.create_task(self._run_background_task())

    async def add_task(self, name, gen):
        """Add a new task to the manager."""
        await self.task_queue.put(self._taskify(name, gen))

    async def _taskify(self, name, gen):
        counter = 0
        async for value in gen:
            await self.output_queue.put((name, value))
            counter += 1
            if counter > 100:
                await asyncio.sleep(0)
                counter = 0
        await self.output_queue.put((name, None))

    async def _run_background_task(self):
        while True:
            coro = await self.task_queue.get()
            if coro is None:  # Sentinel value to stop worker
                await asyncio.gather(*self.tasks)
                await self.output_queue.put(None)
                break
            task = asyncio.create_task(coro)
            self.tasks.append(task)

    async def yield_results(self):
        """Call this method when you are done adding tasks."""
        # Inform the worker to stop listening for new tasks
        await self.task_queue.put(None)
        while True:
            item = await self.output_queue.get()
            yield item
            if item is None:
                break

        # Should not be necesary
        await self.background_task


async def gen_pressure_chart(aconn):
    async with aconn.cursor() as cur:
        await cur.execute(PRESSURE_SELECT)

        async for record in cur:
            bucket, pressure = record
            yield {"time": int(bucket), "pressure": float(pressure)}


async def gen_barometer_chart(q, aconn):
    async with aconn.cursor() as cur:
        await cur.execute(PRESSURE_SELECT)

        async for record in cur:  # Iterate directly over the cursor
            bucket, pressure = record
            await q.put(
                ["barometer", {"time": int(bucket), "pressure": float(pressure)}]
            )

        await q.put(["barometer", "STOP"])


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
    task_man = TaskMan()
    async with await psycopg.AsyncConnection.connect(**db_args) as aconn:
        await task_man.add_task("summary", get_summary(aconn))
        await task_man.add_task("barometer", gen_pressure_chart(aconn))
        async for item in task_man.yield_results():
            output(item)


async def get_summary(aconn):
    tasks = [
        get_stormwatch(aconn),
        get_current(aconn),
    ]
    for task in asyncio.as_completed([*tasks]):
        yield await task


THRESHOLDS = [
    (-1.0, "Storm's abrewin'"),
    (-0.5, "Weather incoming"),
    (0.5, "Clouds clearing"),
    (float("inf"), "Blue skies"),
]


async def get_current(aconn):
    columns = [
        "time",
        "outdoor_temp",
        "humidity",
        "uvi",
        "rain_rate",
    ]

    def convert(key, val):
        if key == "time":
            return "last_entry", val.timestamp()
        elif key == "outdoor_temp":
            return key, float(val)
        else:
            return key, int(val)

    placeholders = ", ".join(columns)
    query = f"""
        SELECT {placeholders}
        FROM weather ORDER BY time DESC LIMIT 1;
    """
    async with aconn.cursor() as cur:
        await cur.execute(query)
        result = await cur.fetchone()
    assert result
    return {
        key: value for key, value in map(lambda kv: convert(*kv), zip(columns, result))
    }


async def get_yesterday():
    pass


async def get_stormwatch(aconn):
    # SQL query using time bucketing and calculating averages
    query = """
        WITH PressureBuckets AS (
            SELECT
                time_bucket('10 minutes', time) as bucket,
                AVG(pressure) as avg_pressure
            FROM weather
            WHERE time >= NOW() - INTERVAL '2 hours'
            GROUP BY bucket
            ORDER BY bucket DESC
        )
        SELECT
            (SELECT avg_pressure FROM PressureBuckets LIMIT 1) AS current_pressure,
            (SELECT avg_pressure FROM PressureBuckets OFFSET 6 LIMIT 1) AS one_hour_ago_pressure
        FROM PressureBuckets
        LIMIT 1;
    """

    async with aconn.cursor() as cur:
        await cur.execute(query)
        result = await cur.fetchone()
    assert result
    current, one_hour_ago = result
    pressure_change = current - one_hour_ago
    for threshold, message in THRESHOLDS:
        if pressure_change <= threshold:
            return {"stormwatch": message}


asyncio.run(main())
