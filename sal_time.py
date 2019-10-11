import time

import SALPY_ATHeaderService

mgr = SALPY_ATHeaderService.SAL_ATHeaderService()
now_sys = time.time()
now_sal = mgr.getCurrentTime()
print(f"System time: {now_sys}")
print(f"SAL time: {now_sal}") 
delta_t = now_sal - now_sys
print(f"Delta T: {delta_t}")
