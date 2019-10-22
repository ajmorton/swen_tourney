"""
The list of submitters who have received an extension beyond the submission close date.
"""
import json
import os
from datetime import datetime

from tournament.config.exceptions import NoConfigDefined
from tournament.config.files import ApprovedSubmitters
from tournament.util import paths, format as fmt, Submitter, Result


class SubmitterExtensions:
    """ The list of submitters who have received an extension in the tournament """

    default_extension_details = {
        'extension_deadline': datetime.strftime(datetime.max, fmt.DATETIME_TRACE_STRING),
        'submitters': ["student_a", "student_b", "student_c"]
    }

    extension_details = {}

    def __init__(self):
        if not os.path.exists(paths.SUBMITTER_EXTENSIONS_LIST):
            self.write_default()
            raise NoConfigDefined("No submitters extensions list found at {}. A default one has been created"
                                  .format(paths.SUBMITTER_EXTENSIONS_LIST))
        else:
            self.extension_details = json.load(open(paths.SUBMITTER_EXTENSIONS_LIST, 'r'))

    def is_eligible(self, submitter: Submitter) -> bool:
        """ Check whether a submitter is eligible for an extension """
        return submitter in self.extension_details['submitters'] and not self.extensions_closed()

    def write_default(self):
        """ Create a default ApprovedSubmitters file """
        json.dump(self.default_extension_details, open(paths.SUBMITTER_EXTENSIONS_LIST, 'w'), indent=4, sort_keys=True)

    def extensions_closed(self) -> bool:
        """ Check whether the extensions deadline has passed """
        return datetime.now() > datetime.strptime(self.extension_details['extension_deadline'],
                                                  fmt.DATETIME_TRACE_STRING)

    def check_non_default(self) -> Result:
        """ Check the list of submitters extensions has been filled with non-default values """
        if self.extension_details != SubmitterExtensions.default_extension_details:
            return Result(True, "Non-default submitter extensions file is present:")
        else:
            return Result(False, "ERROR: Submitter extensions list has not been changed from the default provided.\n"
                                 "       Please update {} with the correct details"
                          .format(paths.SUBMITTER_EXTENSIONS_LIST))

    def check_submitters_exist(self) -> Result:
        """ Check that all submitter in SubmitterExtensions are approved submitters in the tournament """
        unknown_submitters = [sub for sub in self.extension_details['submitters']
                              if sub not in ApprovedSubmitters().get_list()]
        if unknown_submitters:
            return Result(False,
                          "\tERROR: Submitters {} not found in approved submitters list".format(unknown_submitters))
        else:
            return Result(True, '')

    def check_valid(self) -> Result:
        """ Check the approved submitters list is valid """
        if ApprovedSubmitters().submissions_closed():
            result = self.check_non_default()
            if result:
                result += self.check_submitters_exist()
            return result
        else:
            return Result(True, "")
