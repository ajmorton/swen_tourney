""" Main commands sent to the tournament """

import os
import subprocess
import time
from datetime import datetime

from tournament import config as cfg
from tournament import flags, daemon
from tournament import processing as tourney
from tournament.config import ApprovedSubmitters, SubmitterExtensions
from tournament.reporting import results_server
from tournament.util import paths
from tournament.util.types import Result


def start_tournament() -> Result:
    """ Start the tournament daemon and results server threads """
    if daemon.is_alive():
        return Result(False, "Tournament already online")

    result = cfg.configuration_valid()
    if result:
        result += daemon.start()
        if result:
            time.sleep(1)
            result += results_server.start_server()
    return result


def shutdown(message: str = "") -> Result:
    """ Shutdown the tournament. Optionally provide a message to display while offline """
    return daemon.shutdown(message)


def clean() -> Result:
    """ Remove all submissions, config files, and state from the tournament """
    result = daemon.is_alive()
    if result:
        return Result(False, result.traces + "Current submissions should not be removed unless the server is offline")

    subprocess.run(f"rm -rf {paths.SUBMISSIONS_DIR}/*/*", shell=True, check=True)
    subprocess.run(f"rm -f  {paths.TRACES_DIR}/*.log", shell=True, check=True)
    subprocess.run(f"rm -f  {paths.STATE_DIR}/**.json", shell=True, check=True)
    subprocess.run(f"rm -f  {paths.STATE_DIR}/**/*.json", shell=True, check=True)
    subprocess.run(f"rm -f  {paths.DIFF_FILE}", shell=True, check=True)
    flags.clear_all_flags()

    return Result(True, "All submissions and tournament results have been deleted")


def get_diffs() -> Result:
    """ Fetch diffs of submitters progs, provided submissions have been closed """
    if ApprovedSubmitters().submissions_closed() and SubmitterExtensions().extensions_closed():
        return tourney.get_diffs()
    else:
        return Result(False, "Submissions are not currently closed.\n"
                             "get_diffs should only be called once submissions are closed")


def rescore_invalid_progs() -> Result:
    """ rescore programs based on the results of the annotated diffs file, provided submissions are closed """
    if not ApprovedSubmitters().submissions_closed() or not SubmitterExtensions().extensions_closed():
        return Result(False, "Submissions are not currently closed.\n "
                             "Rescoring invalid programs should only be performed once submissions are closed")

    if not os.path.exists(paths.DIFF_FILE):
        return Result(False, f"Error the diff file '{paths.DIFF_FILE}' does not exist.\n"
                             f"Make sure to run 'get_diffs' and update the resulting file before running "
                             f"this command.")

    return tourney.rescore_invalid_progs()


def create_results_csv() -> Result:
    """ Generate a csv containing student results """

    if not ApprovedSubmitters().submissions_closed():
        return Result(False, "Cannot export results. Submissions are still open")

    if not SubmitterExtensions().extensions_closed():
        return Result(False, "Cannot export results. Submissions are still open for students with an extension")

    return tourney.create_results_csv()
