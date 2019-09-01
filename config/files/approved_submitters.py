from config.exceptions import NoConfigDefined
import os
import json
from util import paths
from util.types import Submitter
from typing import Dict


class ApprovedSubmitters:

    default_approved_submitters = {
        "student_a": {'student_id': "123456"},
        "student_b": {'student_id': "234567"},
        "student_c": {'student_id': "345678"}
    }

    approved_submitters = {}

    def __init__(self):
        if not os.path.exists(paths.APPROVED_SUBMITTERS_LIST):
            ApprovedSubmitters.write_default()
            raise NoConfigDefined("No approved submitters file found at {}. A default one has been created"
                                  .format(paths.APPROVED_SUBMITTERS_LIST))
        else:
            self.approved_submitters = json.load(open(paths.APPROVED_SUBMITTERS_LIST, 'r'))

    def get_list(self) -> Dict[Submitter, dict]:
        return self.approved_submitters

    def get_submitter_username(self, submitter: str) -> (bool, Submitter):
        """
        Submitters can be identified either by their username or by their student id.
        Map these to their username
        :param submitter: The username or student id of the submitter
        :return: Whether a valid username was found, and the username if found
        """
        for elig_submitter in self.approved_submitters:
            if submitter == elig_submitter.lower() or \
               submitter.lower() == self.approved_submitters[elig_submitter]['student_id']:
                return True, elig_submitter

        # else elig_submitter not found
        return False, ""

    @staticmethod
    def write_default():
        json.dump(ApprovedSubmitters.default_approved_submitters, open(paths.APPROVED_SUBMITTERS_LIST, 'w'),
                  indent=4, sort_keys=True)

    def check_non_default(self) -> bool:
        if self.approved_submitters != ApprovedSubmitters.default_approved_submitters:
            print("Approved submitters file format has been written:")
            return True
        else:
            print("ERROR: Approved submitters list has not been changed from the default provided.\n"
                  "       Please update {} with the correct details"
                  .format(paths.APPROVED_SUBMITTERS_LIST))

    def check_num_submitters(self) -> bool:
        num_submitters = len(self.approved_submitters)
        if num_submitters < 2:
            print("\tERROR: There are less than 2 submitters in the approved submitters list")
            return False
        else:
            print("\tThere are {} approved submitters for the tournament".format(num_submitters))
            return True

    def check_valid(self) -> bool:

        valid = self.check_non_default()

        if valid:
            valid = self.check_num_submitters()

        print()
        return valid
