import SALPY_Test
from lsst.ts.salobj import Remote
import asyncio
r = Remote(SALPY_Test, 1)

while True:
    print(asyncio.get_event_loop().run_until_complete(r.evt_heartbeat.next(flush=False)))
