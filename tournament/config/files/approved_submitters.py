"""
The list of approved submitters for the tournament.
Students are identified by their student username, but Gitlab accounts may also be created based on other details such
as student id so additional information is provided to help map between a students Gitlab username and their student
username
"""
import json
import os
from datetime import datetime

from tournament.config.exceptions import NoConfigDefined
from tournament.util import format as fmt
from tournament.util import paths, Submitter, Result


class ApprovedSubmitters:
    """ The list of approved submitters in the tournament """

    default_submitters_details = {
        'submission_deadline': datetime.strftime(datetime.max, fmt.DATETIME_TRACE_STRING),
        'submission_extensions_deadline': datetime.strftime(datetime.max, fmt.DATETIME_TRACE_STRING),
        'submitters': {
            "student_a": {"extension_granted": False},
            "student_b": {"extension_granted": False},
            "student_c": {"extension_granted": False},
        }
    }

    submitters_details = {}

    def __init__(self):
        if not os.path.exists(paths.APPROVED_SUBMITTERS_LIST):
            ApprovedSubmitters._write_default()
            raise NoConfigDefined(f"No approved submitters file found at {paths.APPROVED_SUBMITTERS_LIST} . "
                                  f"A default one has been created")
        else:
            self.submitters_details = json.load(open(paths.APPROVED_SUBMITTERS_LIST, 'r'))

    def get_list(self) -> [Submitter]:
        """ Get the list of approved submitters """
        return self.submitters_details['submitters'].keys()

    def elig_for_extension(self, submitter: Submitter) -> bool:
        """ Return true if the submitter has an extension """
        return self.submitters_details['submitters'][submitter]['extension_granted'] and not self.extensions_closed()

    def submissions_closed(self) -> bool:
        """ Check whether the submission deadline has passed """
        return datetime.now() > datetime.strptime(self.submitters_details['submission_deadline'],
                                                  fmt.DATETIME_TRACE_STRING)

    def extensions_closed(self) -> bool:
        """ Check whether the submission extension deadline has passed """
        return datetime.now() > datetime.strptime(self.submitters_details['submission_extensions_deadline'],
                                                  fmt.DATETIME_TRACE_STRING)

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
            return Result(False, f"ERROR: Approved submitters list has not been changed from the default provided.\n"
                                 f"Please update {paths.APPROVED_SUBMITTERS_LIST} with the correct details")

    def _check_extension_date(self) -> Result:
        """ Check that the extension deadline is after the submission deadline """
        submission_deadline = datetime.strptime(self.submitters_details['submission_deadline'],
                                                fmt.DATETIME_TRACE_STRING)
        extension_deadline = datetime.strptime(self.submitters_details['submission_extensions_deadline'],
                                               fmt.DATETIME_TRACE_STRING)
        if extension_deadline > submission_deadline:
            return Result(True, "\tExtension deadline is after submission deadline")
        else:
            return Result(False, "\tERROR: Extension deadline is not after the submission deadline")

    def check_valid(self) -> Result:
        """ Check the approved submitters list is valid """
        result = self._check_non_default()
        if result:
            result += self._check_extension_date() + ""
        return result
