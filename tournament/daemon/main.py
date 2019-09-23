"""
Submissions and report requests are made to the tournament asynchronously by placing them in the paths.STAGED_DIR
folder. These are then popped by the tournament daemon, oldest timestamp first, and processed in the tournament.
"""
import subprocess
from datetime import datetime
from time import sleep, time
import re
from multiprocessing import Pool

from tournament.main import main as tourney
from tournament.config import AssignmentConfig
from tournament.daemon import flags, fs
from tournament.daemon.flags import Flag
from tournament.main.tourney_snapshot import TourneySnapshot
from tournament.util import FilePath, Result
from tournament.util import paths, format as fmt, print_tourney_trace, print_tourney_error


# When processing submissions testing can be parallelised. Instantiate thread pool here.
pool = Pool()


def process_report_request(file_path: FilePath):
    """
    Provided a report request from paths.STAGED_DIR, create a snapshot of the current tournament state and write a
    .csv report with submitter scores
    :param file_path: the file path of the report request in paths.STAGED_DIR
    """
    report_time = fs.get_report_request_time(file_path)
    print_tourney_trace("Generating report for tournament submissions as of {}".format(report_time))
    snapshot = TourneySnapshot(report_time=report_time)
    snapshot.write_csv()
    subprocess.run("rm -f {}".format(file_path), shell=True)


def process_submission_request(file_path):
    """ Provided a submission from paths.STAGED_DIR, process the submission in the tournament """
    (submitter, submission_time) = fs.get_submission_request_details(file_path)

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


def check_submission_file_size(pre_val_dir: FilePath) -> Result:
    """ Check that the size of the submissions is not too large """
    result = subprocess.run("du -sh {}".format(pre_val_dir),
                            stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    filesize_pattern = "^([0-9]+(?:\.[0-9]+)?)([BKMG])"  # number and scale, eg: "744K" = 744KB or "1.8G" == 1.8GB
    submission_size_regex = re.search(filesize_pattern, result.stdout)

    if submission_size_regex is not None:
        size_in_bytes = float(submission_size_regex.group(1)) * \
                        {"B": 1, "K": 1000, "M": 1000000, "G": 1000000000}.get(submission_size_regex.group(2))
        if size_in_bytes > 150 * 1000 * 1000:  # 150 MB
            error_string = "Error: After compilation and test generation the submission file size ({}) is larger than "\
                           "150 megabytes.\nServer space is limited so please keep your submissions to a " \
                           "reasonable size".format("".join(submission_size_regex.groups()))
            error_string += "Further details:\n{}".format(
                subprocess.run("du -d 2 -h .", cwd=pre_val_dir, shell=True, universal_newlines=True,
                               stdout=subprocess.PIPE).stdout)

            return Result((False, error_string))
    return Result((True, "submission size valid"))


def is_alive() -> Result:
    """ Check if the TourneyDaemon is online via the alive flag """
    if flags.get_flag(Flag.ALIVE):
        if flags.get_flag(Flag.SHUTTING_DOWN):
            return Result((True, "Tournament is online, but in the process of shutting down"))
        else:
            return Result((True, "Tournament is online"))
    else:
        return Result((False, "Tournament is not online"))


def shutdown() -> Result:
    """ Set the shutdown flag for TourneyDaemon """
    if not flags.get_flag(Flag.ALIVE):
        return Result((False, "Tournament is already offline"))
    else:
        flags.set_flag(Flag.SHUTTING_DOWN, True)
        print_tourney_trace("Shutdown event received. Finishing processing")
        return Result((True, "Tournament is shutting down. "
                             "This may take a while as current processing must be completed.\n"
                             "Check the tournament traces to see when the tournament has successfully stopped."))


def make_report_request(request_time: datetime) -> Result:
    """ Create a report request file in paths.STAGED_DIR """
    fs.create_report_request(request_time)
    trace = "Report request made at {}".format(request_time.strftime(fmt.DATETIME_TRACE_STRING))
    print_tourney_trace(trace)
    return Result((True, trace))


def close_submissions() -> Result:
    """ Set the SUBMISSIONS_CLOSED flag to prevent any further submissions """
    flags.set_flag(flags.Flag.SUBMISSIONS_CLOSED, True)
    return Result((True, "Submissions closed"))


def start():
    """ Start a new thread and run the TourneyDaemon in it """
    subprocess.Popen("python3 -m tournament.daemon.main", cwd=paths.ROOT_DIR, shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Result((True, "Tournament starting.\nTraces are being written to {}".format(paths.TRACE_FILE)))


def main():
    """
    TourneyDaemon constantly polls the paths.STAGED_DIR for files. If present, the oldest file
    (i.e. the earliest submission) is popped and processed.
    """
    print_tourney_trace("TourneyDaemon started...")

    try:
        flags.set_flag(Flag.ALIVE, True)

        # Create a report file on startup
        TourneySnapshot(report_time=datetime.now()).write_snapshot()

        while not flags.get_flag(Flag.SHUTTING_DOWN):

            if not flags.get_flag(Flag.ALIVE):
                # In the event of an uncaught crash the ALIVE flag can be manually deleted to kill the tournament
                break

            next_submission_to_process = fs.get_next_request()

            if next_submission_to_process:
                file_path = paths.STAGING_DIR + "/" + next_submission_to_process
                if fs.is_report(file_path):
                    process_report_request(file_path)
                elif fs.is_submission(file_path):
                    process_submission_request(file_path)
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
    flags.set_flag(Flag.ALIVE, False)
    flags.set_flag(Flag.SHUTTING_DOWN, False)


if __name__ == '__main__':
    main()
