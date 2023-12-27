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
def gen_barometer_chart(conn):
    with conn.cursor() as cur:
        cur.execute(PRESSURE_SELECT)
        
        for record in cur:  # Iterate directly over the cursor
            bucket, pressure = record
            # yield ['barometer', bucket, str(pressure)]
            yield ['barometer', int(bucket), float(pressure)]


async def gen_pressure(q, id):
    await q.put([ id, 'x', {"foo": "far"}])
    await asyncio.sleep(1)
    await q.put([ id, 'y', {"boo": "bar"}])
    await asyncio.sleep(1)
    await q.put([ id, 'z', {"boo": "bar"}])
    await asyncio.sleep(1)
    await q.put([ id, 'zz', {"boo": "bar"}])
    await asyncio.sleep(1)
    await q.put([ id, 'zzz', {"boo": "bar"}])

def output(item):
    print(f"data: {json.dumps(item)}\n\n", flush=True)

async def gather(q, producers):
    await asyncio.gather(*producers)
    await q.put("STOP")
    
async def main():
    q = asyncio.Queue()
    # List of async methods to run in the background
    producers = [gen_pressure(q, 'a'), gen_pressure(q, 'b')]
    asyncio.create_task(gather(q, producers))
    while True:
        item = await q.get()
        output(item)
        if item == "STOP":
            break


# Running the main coroutine and getting the results
asyncio.run(main())




# def gen_events():
#     conn = psycopg2.connect(**{
#         "dbname": "monitoring",
#         "user": "adam",
#         "password": "adam",
#         "host": "haus.local",
#     })
#     yield from gen_barometer_chart(conn)
