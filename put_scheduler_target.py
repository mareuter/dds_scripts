import argparse
import SALPY_scheduler
import sqlite3
import sys

# Don't want to depend on builtins
try:
    rin = raw_input
except NameError:
    rin = input

SQL = "select * from TargetHistory"
SQL_EXPS = "select * from TargetExposures where TargetHistory_targetId={}"

def get_exposure_times(tid, cur):
    query = SQL_EXPS.format(tid)
    cur.execute(query)
    return cur.fetchall()

def target_from_row(r, exp_times, salobj):
    salobj.targetId = r[0]
    salobj.fieldId = r[2]
    salobj.groupId = r[3]
    salobj.filter = str(r[4])
    salobj.request_time = r[5]
    salobj.request_mjd = r[6]
    salobj.ra = r[7]
    salobj.dec = r[8]
    salobj.angle = r[9]
    salobj.num_exposures = r[10]
    for i, exp_time in enumerate(exp_times):
        salobj.exposure_times[i] = int(exp_time[3])

if __name__ == "__main__":

    description = ["Python script to serve an OpSim4 SQLite database like a "]
    description.append("DDS event stream. It does this in a manual fashion by ")
    description.append("requiring a Enter key press to publish the next target.")

    parser = argparse.ArgumentParser(description=" ".join(description))
    parser.add_argument("dbfile", help="The full path to the OpSim SQLite "
                        "database file.")
    parser.add_argument("-l", "--limit", default=100, help="Look at the first N "
                        "fields.")
    parser.set_defaults()
    args = parser.parse_args()

    query = SQL + " limit {}".format(args.limit)
    cursor = None
    with sqlite3.connect(args.dbfile) as conn:
        cursor = conn.cursor()
        cursor.execute(query)

    try:
        manager = SALPY_scheduler.SAL_scheduler()
        manager.setDebugLevel(0)
        manager.salTelemetryPub("scheduler_target")

        target = SALPY_scheduler.scheduler_targetC()

        rows = cursor.fetchall()
        for row in rows:
            exposure_times = get_exposure_times(row[0], cursor)
            target_from_row(row, exposure_times, target)
            manager.putSample_target(target)
            response = rin("Target served. Press Enter for next target.")
            if response != "":
                raise KeyboardInterrupt

        manager.salShutdown()

    except KeyboardInterrupt:
        manager.salShutdown()
        sys.exit(0)
