"""
Submissions ready to be processed are placed into paths.STAGED_DIR and their details are encoded in their file names
in the file system. The tournament daemon will then pop from this queue by the oldest submission and process it.
"""
import os
import subprocess
from datetime import datetime

from tournament.flags import get_flag, set_flag, SubmissionFlag
from tournament.util import FilePath, Submitter, Result
from tournament.util import format as fmt, paths, print_tourney_trace

SUBMISSION_REQUEST_PREFIX = "submission."


def get_next_request() -> FilePath:
    """
    Pop the next submission to process in paths.STAGED_DIR
    :return: the file path of the next submission to process
    """
    # get files ordered by creation date
    submissions = [file for file in sorted(os.scandir(paths.STAGING_DIR), key=lambda folder: folder.stat().st_mtime)
                   if file.name != ".gitignore"]

    return submissions[0].name if submissions else FilePath("")


def _remove_previous_occurrences(submitter: Submitter):
    """
    To reduce computation load on the tournament server, a submitters prior submissions will be removed from the queue
    when they make a new submission.

    :param submitter: the submitter making a new submission
    """
    submissions = sorted(os.scandir(paths.STAGING_DIR), key=lambda folder: folder.stat().st_mtime, reverse=True)
    submissions = [file for file in submissions if file.name != ".gitignore"]

    for submission in submissions:
        (sub, _) = get_submission_request_details(submission)
        if sub == submitter:
            subprocess.run(f"rm -rf {paths.STAGING_DIR}/{submission}", shell=True, check=True)


def is_submission(file_path: FilePath) -> bool:
    """ Return whether a file is a submission """
    file_name = os.path.basename(file_path)
    return file_name.startswith(SUBMISSION_REQUEST_PREFIX) and get_flag(SubmissionFlag.SUBMISSION_READY, file_path)


def _create_submission_request_name(submitter: Submitter, submission_time: datetime) -> FilePath:
    """
    Take a submission and its submission date and create a folder name from them.
    e.g. submitter: student_a, submission_time: 2019.09.08_12.00 --> student_a.2019_09_08__12_00
    :param submitter: the submitter making the submission
    :param submission_time: the time of the submission
    :return: the folder name for the new submission
    """
    return FilePath(f"{SUBMISSION_REQUEST_PREFIX + submitter}.{submission_time.strftime(fmt.DATETIME_FILE_STRING)}")


def get_submission_request_details(file_path: FilePath) -> (Submitter, datetime):
    """
    Extract the details of a submission from its folder name
    :param file_path: the path of the submission to extract information from
    :return: the name of the submitter and the date the submission was made
    """
    folder_name = os.path.basename(file_path)
    split = folder_name.split(".")
    # submitter name may contain a full stop. We can assume that the first element in split is the token
    # "submission", and the last element is the submission time. So everything in between is the submitter name
    submitter = ".".join(split[1:-1])
    submission_time = datetime.strptime(split[-1], fmt.DATETIME_FILE_STRING)

    return submitter, submission_time


def queue_submission(submitter: Submitter, submission_time: datetime) -> Result:
    """ Create a submission for a submitter in the paths.STAGED_DIR """

    pre_val_dir = paths.get_pre_validation_dir(submitter)

    staged_dir = f"{paths.STAGING_DIR}/{_create_submission_request_name(submitter, submission_time)}"
    _remove_previous_occurrences(submitter)
    subprocess.run(f"mv {pre_val_dir} {staged_dir}", shell=True, check=True)
    set_flag(SubmissionFlag.SUBMISSION_READY, True, staged_dir)

    trace = f"Submission successfully made by {submitter} at {submission_time.strftime(fmt.DATETIME_TRACE_STRING)}"
    print_tourney_trace(trace)
    return Result(True, trace)
