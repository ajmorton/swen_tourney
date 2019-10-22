"""
Submissions and report requests are made to the tournament asynchronously by placing them in the paths.STAGED_DIR
folder. These are then popped by the tournament daemon, oldest timestamp first, and processed in the tournament.
"""
import subprocess
from datetime import datetime
from multiprocessing import Pool, current_process, Value
from time import sleep, time

from tournament import processing as tourney
from tournament.config import AssignmentConfig
from tournament.daemon import fs_queue
from tournament.flags import get_flag, set_flag, TourneyFlag
from tournament.processing import TourneySnapshot
from tournament.util import FilePath, Result
from tournament.util import paths, format as fmt, print_tourney_trace, print_tourney_error


def set_process_name(counter):
    """ Set the name of each process in the pool, making use of a shared counter between all processes """
    with counter.get_lock():
        current_process().name = "process_" + str(counter.value)
        counter.value = counter.value + 1


# When processing submissions testing can be parallelised. Instantiate thread pool here.
# initargs contains a concurrency safe counter, used by set_process_name
pool = Pool(initializer=set_process_name, initargs=(Value('i', 0, lock=True),))


def _process_report_request(file_path: FilePath):
    """
    Provided a report request from paths.STAGED_DIR, create a snapshot of the current tournament state and write a
    .csv report with submitter scores
    :param file_path: the file path of the report request in paths.STAGED_DIR
    """
    report_time = fs_queue.get_report_request_time(file_path)
    print_tourney_trace("Generating report for tournament submissions as of {}".format(report_time))
    snapshot = TourneySnapshot(report_time=report_time)
    snapshot.write_csv()
    subprocess.run("rm -f {}".format(file_path), shell=True)


def _process_submission_request(file_path):
    """ Provided a submission from paths.STAGED_DIR, process the submission in the tournament """
    (submitter, submission_time) = fs_queue.get_submission_request_details(file_path)

    staged_dir = file_path
    tourney_dest = paths.get_tourney_dir(submitter)

    assg = AssignmentConfig().get_assignment()
    new_tests = assg.detect_new_tests(staged_dir, FilePath(tourney_dest))
    new_progs = assg.detect_new_progs(staged_dir, FilePath(tourney_dest))

    subprocess.run("rm -rf {}".format(tourney_dest), shell=True)
    subprocess.run("mv {} {}".format(staged_dir, tourney_dest), shell=True)

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
            return Result(False, "Tournament is shutdown: {}".format(is_shutdown.traces))
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


def make_report_request(request_time: datetime) -> Result:
    """ Create a report request file in paths.STAGED_DIR """
    fs_queue.create_report_request(request_time)
    trace = "Report request made at {}".format(request_time.strftime(fmt.DATETIME_TRACE_STRING))
    print_tourney_trace(trace)
    return Result(True, trace)


def start() -> Result:
    """ Start a new thread and run the TourneyDaemon in it """
    subprocess.Popen("python3 -m tournament.daemon.main", cwd=paths.ROOT_DIR, shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Result(True, "Tournament starting.\nTraces are being written to {}".format(paths.TRACE_FILE))


def main():
    """
    TourneyDaemon constantly polls the paths.STAGED_DIR for files. If present, the oldest file
    (i.e. the earliest submission) is popped and processed.
    """
    print_tourney_trace("TourneyDaemon started...")

    try:
        set_flag(TourneyFlag.ALIVE, True)
        set_flag(TourneyFlag.SHUTDOWN, False)

        # Create a report file on startup
        TourneySnapshot(report_time=datetime.now()).write_snapshot()

        while not get_flag(TourneyFlag.SHUTDOWN):

            if not get_flag(TourneyFlag.ALIVE):
                # In the event of an uncaught crash the ALIVE flag can be manually deleted to kill the tournament
                break

            next_submission_to_process = fs_queue.get_next_request()

            if next_submission_to_process:
                file_path = paths.STAGING_DIR + "/" + next_submission_to_process
                if fs_queue.is_report(file_path):
                    _process_report_request(file_path)
                elif fs_queue.is_submission(file_path):
                    _process_submission_request(file_path)
                else:
                    # submission is present in the staged folder, but has not finished being copied across
                    print_tourney_trace("Request present but not valid: {}".format(next_submission_to_process))
                    sleep(5)
            else:
                print_tourney_trace("Nothing to process")
                sleep(60)
    except Exception as exception:  # pylint: disable=broad-except
        print_tourney_error("Exception caught while running tournament")
        print_tourney_error(str(exception))
        import traceback
        print_tourney_error(traceback.format_exc())
        # emailer.email_crash_report()

    # shutdown hook
    print_tourney_trace("TourneyDaemon shutting down.")
    set_flag(TourneyFlag.ALIVE, False)


if __name__ == '__main__':
    main()
