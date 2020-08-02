"""
The list of approved submitters for the tournament.
Students are identified by their student username, but Gitlab accounts may also be created based on other details such
as student id so additional information is provided to help map between a students Gitlab username and their student
username
"""
import json
import os
from datetime import datetime
from typing import Dict

from tournament.config.exceptions import NoConfigDefined
from tournament.util import format as fmt
from tournament.util import paths, Submitter, Result


class ApprovedSubmitters:
    """ The list of approved submitters in the tournament """

    default_submitters_details = {
        'submission_deadline': datetime.strftime(datetime.max, fmt.DATETIME_TRACE_STRING),
        'submitters': {
            "student_a": {'student_id': "123456"},
            "student_b": {'student_id': "234567"},
            "student_c": {'student_id': "345678"}}}

    submitters_details = {}

    def __init__(self):
        if not os.path.exists(paths.APPROVED_SUBMITTERS_LIST):
            ApprovedSubmitters._write_default()
            raise NoConfigDefined("No approved submitters file found at {} . A default one has been created"
                                  .format(paths.APPROVED_SUBMITTERS_LIST))
        else:
            self.submitters_details = json.load(open(paths.APPROVED_SUBMITTERS_LIST, 'r'))

    def get_list(self) -> Dict[Submitter, dict]:
        """ Get the list of approved submitters """
        return self.submitters_details['submitters']

    def submissions_closed(self) -> bool:
        """ Check whether the submission deadline has passed """
        return datetime.now() > datetime.strptime(self.submitters_details['submission_deadline'],
                                                  fmt.DATETIME_TRACE_STRING)

    def get_submitter_username(self, submitter: str) -> (bool, Submitter):
        """
        Submitters can be identified either by their username or by their student id.
        Map these to their username
        :param submitter: The username or student id of the submitter
        :return: Whether a valid username was found, and the username if found
        """
        for elig_submitter in self.submitters_details['submitters']:
            if submitter.lower() in [elig_submitter.lower(),
                                     self.submitters_details['submitters'][elig_submitter]['student_id']]:
                return True, elig_submitter

        # else elig_submitter not found
        return False, ""

    @staticmethod
    def _write_default():
        """ Create a default ApprovedSubmitters file """
        json.dump(ApprovedSubmitters.default_submitters_details, open(paths.APPROVED_SUBMITTERS_LIST, 'w'),
                  indent=4, sort_keys=True)

    def _check_non_default(self) -> Result:
        """ Check the list of approved submitters has been filled with non-default values """
        if self.submitters_details != ApprovedSubmitters.default_submitters_details:
            return Result(True, "Non-default approved submitters file is present:")
        else:
            return Result(False, "ERROR: Approved submitters list has not been changed from the default provided.\n"
                                 "Please update {} with the correct details".format(paths.APPROVED_SUBMITTERS_LIST))

    def _check_num_submitters(self) -> Result:
        """ Check that more than one submitter has been added to the approved submitters list """
        num_submitters = len(self.submitters_details['submitters'])
        if num_submitters < 2:
            return Result(False, "\tERROR: There are less than 2 submitters in the approved submitters list")
        else:
            return Result(True, "\tThere are {} approved submitters for the tournament".format(num_submitters))

    def check_valid(self) -> Result:
        """ Check the approved submitters list is valid """
        result = self._check_non_default()
        if result:
            result += self._check_num_submitters() + ""
        return result
