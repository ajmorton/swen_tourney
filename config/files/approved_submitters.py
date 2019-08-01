from config.exceptions import NoConfigDefined
import os
import json
from util import paths


class ApprovedSubmitters:

    default_approved_submitters = {
        "student_a": {'email': "student_a@student.unimelb.edu.au"},
        "student_b": {'email': "student_b@student.unimelb.edu.au"},
        "student_c": {'email': "student_c@student.unimelb.edu.au"},
    }

    approved_submitters = {}

    def __init__(self):
        if not os.path.exists(paths.APPROVED_SUBMITTERS_LIST):
            ApprovedSubmitters.write_default()
            raise NoConfigDefined("No approved submitters file found at {}. A default one has been created"
                                  .format(paths.APPROVED_SUBMITTERS_LIST))
        else:
            self.approved_submitters = json.load(open(paths.APPROVED_SUBMITTERS_LIST, 'r'))

    def get_list(self) -> dict:
        return self.approved_submitters

    @staticmethod
    def write_default():
        json.dump(ApprovedSubmitters.default_approved_submitters, open(paths.APPROVED_SUBMITTERS_LIST, 'w'), indent=4)

    def check_non_default(self) -> bool:
        if self.approved_submitters != ApprovedSubmitters.default_approved_submitters:
            print("Approved submitters file format has been written:")
            return True
        else:
            print("ERROR: Approved submitters list has not been set. Please update {} with the correct details"
                  .format(paths.APPROVED_SUBMITTERS_LIST))

    def check_num_submitters(self):
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

        if valid:
            valid = self.check_submitters_have_emails()

        print()
        return valid

    def check_submitters_have_emails(self) -> bool:
        submitter_list = self.get_list()
        try:
            emails = [submitter_list[submitter]['email'] for submitter in self.get_list()]
            print("\tAll submitters have an associated email")
            return True
        except KeyError:
            print("\tERROR: Some submitters are missing an associated email")
            return False

