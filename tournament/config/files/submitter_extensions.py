"""
The list of submitters who have received an extension beyond the submission close date.
"""
import json
import os

from tournament.config.files import ApprovedSubmitters
from tournament.config.exceptions import NoConfigDefined
from tournament.util import paths, Submitter, Result


class SubmitterExtensions:
    """ The list of submitters who have received an extension in the tournament """

    default_submitter_extensions = [
        "student_a",
        "student_b",
        "student_c"
    ]

    submitter_extensions = []

    def __init__(self):
        if not os.path.exists(paths.SUBMITTER_EXTENSIONS_LIST):
            SubmitterExtensions.write_default()
            raise NoConfigDefined("No submitters extensions list found at {}. A default one has been created"
                                  .format(paths.SUBMITTER_EXTENSIONS_LIST))
        else:
            self.submitter_extensions = json.load(open(paths.SUBMITTER_EXTENSIONS_LIST, 'r'))

    def get_list(self) -> [Submitter]:
        """ Get the list of approved submitters """
        return self.submitter_extensions

    @staticmethod
    def write_default():
        """ Create a default ApprovedSubmitters file """
        json.dump(SubmitterExtensions.default_submitter_extensions, open(paths.SUBMITTER_EXTENSIONS_LIST, 'w'),
                  indent=4, sort_keys=True)

    def check_non_default(self) -> Result:
        """ Check the list of submitters extensions has been filled with non-default values """
        if self.submitter_extensions != SubmitterExtensions.default_submitter_extensions:
            return Result(True, "Non-default submitter extensions file is present:")
        else:
            return Result(False, "ERROR: Submitter extensions list has not been changed from the default provided.\n"
                                 "       Please update {} with the correct details"
                          .format(paths.SUBMITTER_EXTENSIONS_LIST))

    def check_submitters_exist(self) -> Result:
        unknown_submitters = [sub for sub in self.submitter_extensions if sub not in ApprovedSubmitters().get_list()]
        if unknown_submitters:
            return Result(False,
                          "\tERROR: Submitters {} not found in approved submitters list".format(unknown_submitters))
        else:
            return Result(True, '')

    def check_valid(self) -> Result:
        """ Check the approved submitters list is valid """
        return self.check_non_default() + self.check_submitters_exist()
