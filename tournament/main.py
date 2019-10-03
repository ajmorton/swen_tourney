import os

from tournament import config as cfg
from tournament import daemon
from tournament import processing as tourney
from tournament.daemon import flags
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
            result += results_server.start_server()
    return result


def clean() -> Result:
    """ Check that the tournament is in a state to be clean. If so, remove files """
    result = daemon.is_alive()
    if result:
        return Result(False, result.traces + "Current submissions should not be removed unless the server is offline")

    tourney.clean()
    return Result(True, "All submissions and tournament results have been deleted")


def get_diffs() -> Result:
    """ Fetch diffs of submitters progs, provided submissions have been closed """
    if not flags.get_flag(flags.Flag.SUBMISSIONS_CLOSED):
        return Result(False, "Submissions are not currently closed.\n "
                             "get_diffs should only be called once submissions are closed")

    return tourney.get_diffs()


def rescore_invalid_progs() -> Result:
    """ rescore programs based on the results of the annotated diffs file, provided submissions are closed """
    if not flags.get_flag(flags.Flag.SUBMISSIONS_CLOSED):
        return Result(False, "Submissions are not currently closed.\n "
                             "Rescoring invalid programs should only be performed once submissions are closed")

    if not os.path.exists(paths.DIFF_FILE):
        return Result(False, "Error the diff file '{}' does not exist.\n"
                             "Make sure to run 'get_diffs' and update the resulting file before running "
                             "this command.".format(paths.DIFF_FILE))

    return tourney.rescore_invalid_progs()
