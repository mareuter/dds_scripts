import asyncio
import sys

from lsst.ts.salobj import Remote
import SALPY_ATHeaderService

async def transition(state):
    r = Remote(SALPY_ATHeaderService, None)
    print(f"Command to {state}")
    cmd_attr = getattr(r, f"cmd_{state}")
    cmd_data = cmd_attr.DataType()
    if state == 'start':
        cmd_data.settingsToApply = 'default'

    return await cmd_attr.start(cmd_data, timeout=60)

def main(state):
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(transition(state)))

if __name__ == '__main__':
    state = sys.argv[1]
    main(state)
