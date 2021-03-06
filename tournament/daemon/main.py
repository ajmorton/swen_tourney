"""
Submissions are made to the tournament asynchronously by placing them in the paths.STAGED_DIR
folder. These are then popped by the tournament daemon, oldest timestamp first, and processed in the tournament.
"""
import subprocess
from datetime import datetime
from multiprocessing import Pool, current_process, Value
from time import sleep, time
import traceback

from tournament import processing as tourney
from tournament.config import AssignmentConfig
from tournament.daemon import fs_queue
from tournament.flags import get_flag, set_flag, TourneyFlag
from tournament.processing import TourneySnapshot
from tournament.util import FilePath, Result
from tournament.util import paths, format as fmt, print_tourney_trace, print_tourney_error


def _set_process_name(counter):
    """ Set the name of each process in the pool, making use of a shared counter between all processes """
    with counter.get_lock():
        current_process().name = f"process_{str(counter.value)}"
        counter.value = counter.value + 1


def _process_submission_request(file_path, pool):
    """
    Provided a submission from paths.STAGED_DIR, process the submission in the tournament
    :param file_path: the filepath of the submission to process
    :param pool: the threadpool to use for parallel processing
    """
    (submitter, submission_time) = fs_queue.get_submission_request_details(file_path)

    staged_dir = file_path
    tourney_dest = paths.get_tourney_dir(submitter)

    assg = AssignmentConfig().get_assignment()
    new_tests = assg.detect_new_tests(staged_dir, FilePath(tourney_dest))
    new_progs = assg.detect_new_progs(staged_dir, FilePath(tourney_dest))

    subprocess.run(f"rm -rf {tourney_dest}", shell=True, check=True)
    subprocess.run(f"mv {staged_dir} {tourney_dest}", shell=True, check=True)

    time_start = time()
    tourney.run_submission(submitter, submission_time.strftime(fmt.DATETIME_TRACE_STRING), new_tests, new_progs, pool)
    time_end = time()

    snapshot = TourneySnapshot(report_time=submission_time)
    snapshot.set_time_to_process_last_submission(int(time_end - time_start))
    snapshot.write_snapshot()


def is_alive() -> Result:
    """ Check if the TourneyDaemon is online via the alive flag """
    if get_flag(TourneyFlag.ALIVE):
        if get_flag(TourneyFlag.SHUTDOWN):
            return Result(True, "Tournament is online, but in the process of shutting down")
        else:
            return Result(True, "Tournament is online")
    else:
        is_shutdown = get_flag(TourneyFlag.SHUTDOWN)
        if is_shutdown:
            return Result(False, f"Tournament is shutdown: {is_shutdown.traces}")
        else:
            return Result(False, "Tournament is not online")


def shutdown(message: str) -> Result:
    """ Set the shutdown flag for TourneyDaemon """
    if not is_alive():
        return Result(False, "Tournament is already offline")
    else:
        set_flag(TourneyFlag.SHUTDOWN, True, contents=message)
        print_tourney_trace("Shutdown event received. Finishing processing")
        return Result(True, "Tournament is shutting down. "
                            "This may take a while as current processing must be completed.\n"
                            "Check the tournament traces to see when the tournament has successfully stopped.")


def start() -> Result:
    """ Start a new thread and run the TourneyDaemon in it """
    subprocess.Popen("python3.8 -m tournament.daemon.main", cwd=paths.ROOT_DIR, shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Result(True, f"Tournament starting.\nTraces are being written to {paths.TRACE_FILE}")


def main():
    """
    TourneyDaemon constantly polls the paths.STAGED_DIR for files. If present, the oldest file
    (i.e. the earliest submission) is popped and processed.
    """
    print_tourney_trace("TourneyDaemon started...")

    # Thread pool for parallel processing. initargs contains a concurrency safe counter, used by set_process_name
    pool = Pool(initializer=_set_process_name, initargs=(Value('i', 0, lock=True),))

    try:
        set_flag(TourneyFlag.ALIVE, True)
        set_flag(TourneyFlag.SHUTDOWN, False)

        # Create a snapshot file on startup
        TourneySnapshot(report_time=datetime.now()).write_snapshot()

        while not get_flag(TourneyFlag.SHUTDOWN):

            if not get_flag(TourneyFlag.ALIVE):
                # In the event of an uncaught crash the ALIVE flag can be manually deleted to kill the tournament
                break

            next_submission_to_process = fs_queue.get_next_request()

            if next_submission_to_process:
                file_path = f"{paths.STAGING_DIR}/{next_submission_to_process}"
                if fs_queue.is_submission(file_path):
                    _process_submission_request(file_path, pool)
                else:
                    # submission is present in the staged folder, but has not finished being copied across
                    print_tourney_trace(f"Request present but not valid: {next_submission_to_process}")
                    sleep(5)
            else:
                print_tourney_trace("Nothing to process")
                sleep(60)
    except Exception as exception:  # pylint: disable=broad-except
        print_tourney_error("Exception caught while running tournament")
        print_tourney_error(str(exception))
        print_tourney_error(traceback.format_exc())
        # emailer.email_crash_report()

    # shutdown hook
    print_tourney_trace("TourneyDaemon shutting down.")
    set_flag(TourneyFlag.ALIVE, False)


if __name__ == '__main__':
    main()
