from config.exceptions import NoConfigDefined
import os
import json
from util import paths
from util.types import Result


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

    def check_non_default(self) -> Result:
        if self.approved_submitters != ApprovedSubmitters.default_approved_submitters:
            return Result((True, ""))
        else:
            return Result((False, "ERROR: Approved submitters list has not been set.\n"
                                  "       Please update {} with the correct details\n"
                                  .format(paths.APPROVED_SUBMITTERS_LIST)))

