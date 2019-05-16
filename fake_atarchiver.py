import asyncio
from lsst.ts.salobj import Controller
import SALPY_ATArchiver

async def fake_enterControl(id_data):
    print("**********")
    print(f"Moving to standby state.")
    await asyncio.sleep(0.5)
    print("**********")


if __name__ == "__main__":

    print("Starting Controller")
    ata = Controller(SALPY_ATArchiver)
    print("Adding callback")
    ata.cmd_enterControl.callback = fake_enterControl
    print("Run Controller forever")
    asyncio.get_event_loop().run_forever()
