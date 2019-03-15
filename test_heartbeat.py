from lsst.ts import salobj
from lsst.ts import scriptqueue

import SALPY_Test


class TestHeartbeat(scriptqueue.BaseScript):

    def __init__(self, index):
        remote = salobj.Remote(SALPY_Test, 1)
        super().__init__(index=index,
                         descr="Test heartbeat",
                         remotes_dict={"remote": remote})

    async def configure(self, loop_iterations=5):
        self.loop_iterations = int(loop_iterations)

    def set_metadata(self, metadata):
        pass

    async def run(self):
        counter = 0
        while counter < self.loop_iterations:
            data = await self.remote.evt_heartbeat.next(flush=True)
            print(f"Got a heartbeat: {data.heartbeat}")
            counter += 1

if __name__ == '__main__':
    TestHeartbeat.main()
