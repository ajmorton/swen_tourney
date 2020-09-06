"""
This script is designed to emulate the running of a full tournament in order to perform a load test on swen_tourney.
Example submissions with git histories should be placed in the submissions folder.

Note: Due to python namespacing this must be run from the root of the repo with `python3.8 -m test.simulate_tournament`
"""

import os
import subprocess
import time
from collections import Counter
from typing import NamedTuple
from tournament.config import AssignmentConfig
from tournament.util import Ansi

class CommitDetails(NamedTuple):
    """ Details of a commit to replay """
    date: int
    submitter: str
    commit_id: str
    commit_msg: str

    def __repr__(self):
        return f"{self.submitter}: [{self.commit_id}] {self.commit_msg}"

ASSIGNMENT = AssignmentConfig().get_assignment().get_assignment_name()
SUBS_DIR = "./test/submissions"


def verify_submissions_valid() -> bool:
    """ Verify that all submissions are valid to be used for emulating the tournament """

    submitters = [file for file in os.listdir(SUBS_DIR) if not file.startswith(".")]
    submissions_valid = True

    for submitter in submitters:
        expected_submission_path = f"{SUBS_DIR}/{submitter}/{ASSIGNMENT}"
        if not os.path.exists(expected_submission_path):
            print(f"{Ansi.RED}ERROR:{Ansi.END} {expected_submission_path} does not exist")
            submissions_valid = False
            continue
        else:
            git = subprocess.run("git remote -v", shell=True, cwd=expected_submission_path, stdout=subprocess.PIPE,
                                 universal_newlines=True, check=False)
            if ASSIGNMENT not in git.stdout:
                print(f"{Ansi.RED}ERROR:{Ansi.END} {expected_submission_path} does not contain a git history")
                submissions_valid = False

    return submissions_valid


def get_details_all_commits(full_history) -> [CommitDetails]:
    """
    For all submitters in the test/submissions folder get details of all commits in their git histories:
        (date_of_commit, the submitter, the git commit hash)
    :param full_history: Whether all commits in the history of the submission should be extracted, or just the current
    """
    commit_details = []

    submitters = [file for file in os.listdir(SUBS_DIR) if not file.startswith(".")]
    print(f"Simulating tournament for {len(submitters)} submitters")

    for sub in submitters:
        submission_path = f"{SUBS_DIR}/{sub}/{ASSIGNMENT}"
        commits = subprocess.run('git log --first-parent --pretty="format:%at||%h||%s" master -- | sort -r',
                                 cwd=submission_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 universal_newlines=True, check=False).stdout

        if full_history:
            for commit in reversed(commits.strip().split("\n")):
                commit_date, commit_id, commit_msg = commit.split("||")
                commit_details.append(CommitDetails(commit_date, sub, commit_id, commit_msg))
        else:
            commit_date, commit_id, commit_msg = commits.strip().split("\n")[0].split("||")
            commit_details.append(CommitDetails(commit_date, sub, commit_id, commit_msg))

    return sorted(commit_details)


def strip_unneeded_commits(commit_details: [CommitDetails]) -> [CommitDetails]:
    """ Remove unnecessary commit details. If a submitter submits multiple times in a row only keep the most recent """
    stripped = [commit_details[0]]

    # ignore consecutive commits from the same submitter
    for new_commit in commit_details:
        if stripped[-1].submitter is new_commit.submitter:
            stripped[-1] = new_commit
        else:
            stripped.append(new_commit)

    # remove commits common across multiple submissions, these are from the original source assignment
    hash_frequencies = Counter(list(map(lambda x: x.commit_id, commit_details)))
    common_commit_hashes = [hash for (hash, count) in hash_frequencies.items() if count > 50]
    stripped = [commit for commit in stripped if commit.commit_id not in common_commit_hashes]

    print(f"Replaying {len(stripped)} commits")
    return stripped


def make_submission(commit: CommitDetails):
    """
    Given details of a commit checkout the specified commit has for a submitters submission and submit it
    to the tournament
    """

    submitter, commit_id = commit.submitter, commit.commit_id

    subprocess.run(f"git checkout --force {commit_id}", shell=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, cwd=f"{SUBS_DIR}/{submitter}/{ASSIGNMENT}", check=True)

    submission_path = os.path.realpath(f"{SUBS_DIR}/{submitter}/{ASSIGNMENT}")
    subprocess.run(f"./add_sub_manually.sh {submission_path}", shell=True, check=False)


def main():
    """
    For all submissions in test/submissions get their git histories and construct a list of all commits ordered by
    commit date. Then submit each commit in order to the tournament
    """

    while 1:
        answer = input("Would you like replay the entire history of all commits in all submissions, "
                       "or just submit the current version of submissions?\n(full_history/current): ")
        if answer == "full_history":
            full_history = True
            break
        elif answer == "current":
            full_history = False
            break
        else:
            print("Error: unexpected value '{}'. Please choose one of (full_history/current)")

    if not verify_submissions_valid():
        print("Errors must be corrected in test/submissions before testing can be run")
        exit(1)

    if subprocess.run("python3.8 backend.py check_config", shell=True, check=False).returncode != 0:
        print("Error with tournament configuration. Stopping testing")
        exit(1)

    # Ensure tournament is online
    subprocess.run("python3.8 backend.py start_tournament", shell=True, check=False)
    time.sleep(2)

    print()
    print("=========================")
    commit_details = get_details_all_commits(full_history)
    print()
    commit_details = strip_unneeded_commits(commit_details)
    print("=========================")
    print()

    i = 0
    for commit_detail in commit_details:
        i += 1
        print(f"\n({i}/{len(commit_details)}) {commit_detail}")
        make_submission(commit_detail)


if __name__ == '__main__':
    main()
