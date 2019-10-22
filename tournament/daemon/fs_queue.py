"""
Submissions and report request placed into paths.STAGED_DIR and their details are encoded in their file names
in the file system.
    Submissions are named as [SUBMITTER_NAME].[SUBMISSION_DATE] to allow for a submitter to queue multiple submissions
    Reports are names as report_request.[REQUEST_DATE] to allow for the queueing of multiple reports
"""
import os
import subprocess
from datetime import datetime

from tournament.flags import get_flag, set_flag, SubmissionFlag
from tournament.util import FilePath, Submitter, Result
from tournament.util import format as fmt, paths, print_tourney_trace

REPORT_REQUEST_PREFIX = "report_request."
SUBMISSION_REQUEST_PREFIX = "submission."


def get_next_request() -> FilePath:
    """
    Pop the most recent submission or report request in paths.STAGED_DIR
    :return: the file path of the most recent submission or report request
    """
    # get files ordered by creation date
    submissions = [file for file in sorted(os.scandir(paths.STAGING_DIR), key=lambda folder: folder.stat().st_mtime)
                   if file.name != ".gitignore"]

    return submissions[0].name if submissions else FilePath("")


def _remove_previous_occurrences(submitter: Submitter):
    """
    To reduce computation load on the tournament server, a submitters prior submissions will be removed from the queue
    when they make a new submission.
    However, because report requests create a snapshot of the tournament, a submitters prior submission will not be
    removed if a report request has been made in the interim.

    e.g.
    report_request >> submission.1 >> submission.2 --> submission.1 will be removed
    submission.1 >> report_request >> submission.2 --> submission.1 will not be removed due to interim report request

    :param submitter: the submitter making a new submission
    """
    submissions = sorted(os.scandir(paths.STAGING_DIR), key=lambda folder: folder.stat().st_mtime, reverse=True)
    pre_request_submissions = []
    for request in submissions:
        if is_report(request.name) or request.name == ".gitignore":
            break
        else:
            pre_request_submissions.append(request.name)

    for submission in pre_request_submissions:
        (sub, _) = get_submission_request_details(submission)
        if sub == submitter:
            subprocess.run("rm -rf {}".format(paths.STAGING_DIR + "/" + submission), shell=True)


def create_report_request(request_time: datetime):
    """ Create a report request """
    file_name = paths.STAGING_DIR + "/" + REPORT_REQUEST_PREFIX + request_time.strftime(fmt.DATETIME_FILE_STRING)
    subprocess.run("touch {}".format(file_name), shell=True)


def get_report_request_time(file_path: FilePath) -> datetime:
    """ Fetch the time of a queued report request by decoding it from the file name """
    file_name = os.path.basename(file_path)
    [_, request_time] = file_name.split(".")
    return datetime.strptime(request_time, fmt.DATETIME_FILE_STRING)


def is_report(file_path: FilePath) -> bool:
    """ Return whether a file is a report request file """
    file_name = os.path.basename(file_path)
    return file_name.startswith("report_request.")


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
    return FilePath(SUBMISSION_REQUEST_PREFIX + submitter + "." + submission_time.strftime(fmt.DATETIME_FILE_STRING))


def get_submission_request_details(file_path: FilePath) -> (Submitter, datetime):
    """
    Extract the details of a submission from its folder name
    :param file_path: the path of the submission to extract information from
    :return: the name of the submitter and the date the submission was made
    """
    folder_name = os.path.basename(file_path)
    [_, submitter, submission_time] = folder_name.split(".")
    return submitter, datetime.strptime(submission_time, fmt.DATETIME_FILE_STRING)


def queue_submission(submitter: Submitter, submission_time: datetime) -> Result:
    """ Create a submission for a submitter in the paths.STAGED_DIR """

    pre_val_dir = paths.get_pre_validation_dir(submitter)

    staged_dir = paths.STAGING_DIR + "/" + _create_submission_request_name(submitter, submission_time)
    _remove_previous_occurrences(submitter)
    subprocess.run("mv {} {}".format(pre_val_dir, staged_dir), shell=True)
    set_flag(SubmissionFlag.SUBMISSION_READY, True, staged_dir)

    trace = "Submission successfully made by {} at {}".format(submitter,
                                                              submission_time.strftime(fmt.DATETIME_TRACE_STRING))
    print_tourney_trace(trace)
    return Result(True, trace)
