import os
import subprocess
from datetime import datetime

from daemon import flags
from util import format as fmt
from util import paths
from util.types import FilePath, Submitter

REPORT_REQUEST_PREFIX = "report_request."
SUBMISSION_REQUEST_PREFIX = "submission."


def get_next_request() -> FilePath:
    # get files ordered by creation date
    submissions = sorted(os.scandir(paths.STAGING_DIR), key=lambda folder: folder.stat().st_mtime)

    if len(submissions) > 0:
        return submissions[0].name
    else:
        return FilePath("")


def remove_previous_occurrences(submitter: Submitter):
    submissions = sorted(os.scandir(paths.STAGING_DIR), key=lambda folder: folder.stat().st_mtime, reverse=True)
    pre_request_submissions = []
    for request in submissions:
        if is_report(request.name):
            break
        else:
            pre_request_submissions.append(request.name)

    for submission in pre_request_submissions:
        (sub, _) = get_submission_request_details(submission)
        if sub == submitter:
            subprocess.run("rm -rf {}".format(paths.STAGING_DIR + "/" + submission), shell=True)


def create_report_request(request_time: datetime):
    file_name = paths.STAGING_DIR + "/" + REPORT_REQUEST_PREFIX + request_time.strftime(fmt.datetime_file_string)
    subprocess.run("touch {}".format(file_name), shell=True)


def get_report_request_time(file_path: FilePath) -> datetime:
    file_name = os.path.basename(file_path)
    [_, request_time] = file_name.split(".")
    return datetime.strptime(request_time, fmt.datetime_file_string)


def is_report(file_path: FilePath) -> bool:
    file_name = os.path.basename(file_path)
    return file_name.startswith("report_request.")


def is_submission(file_path: FilePath) -> bool:
    file_name = os.path.basename(file_path)
    return file_name.startswith(SUBMISSION_REQUEST_PREFIX) and flags.submission_ready(file_path)


def create_submission_request_name(submitter: Submitter, submission_time: datetime) -> FilePath:
    return FilePath(SUBMISSION_REQUEST_PREFIX + submitter + "." + submission_time.strftime(fmt.datetime_file_string))


def get_submission_request_details(file_path: FilePath) -> (Submitter, datetime):
    folder_name = os.path.basename(file_path)
    [_, submitter, submission_time] = folder_name.split(".")
    return submitter, datetime.strptime(submission_time, fmt.datetime_file_string)
