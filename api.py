from time import sleep

def gen_pressure():
    yield [ 'a', {"foo": "far"}]
    sleep(1)
    yield [ 'b', {"boo": "bar"}]


def gen_events():
    yield from gen_pressure()
    sleep(1)
    yield from gen_pressure()

