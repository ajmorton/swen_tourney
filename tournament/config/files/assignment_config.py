"""
Which assignment the tournament is configured for and validation of these details
"""

import json
import os
from enum import Enum

from tournament.config.assignments import AbstractAssignment, AntAssignment, FuzzAssignment
from tournament.config.exceptions import NoConfigDefined
from tournament.util import paths, Result


class AssignmentType(Enum):
    """ The available assignment types to choose from """
    ant_assignment = AntAssignment
    fuzz_assignment = FuzzAssignment


class AssignmentConfig:
    """ Contains configuration details for which tournament the assignment is set up for. """

    default_assignment_config = {
        'assignment_type': "enter_assignment_type_here",
        'source_assg_dir': "/absolute/path/to/assignment"
    }

    def __init__(self):
        if not os.path.exists(paths.ASSIGNMENT_CONFIG):
            AssignmentConfig._write_default()
            raise NoConfigDefined("No assignment configuration file found at {}. A default one has been created"
                                  .format(paths.ASSIGNMENT_CONFIG))
        else:
            self.config = json.load(open(paths.ASSIGNMENT_CONFIG, 'r'))

    def get_assignment(self) -> AbstractAssignment:
        """ Get which assignment the tournament has been configured for """
        return AssignmentType[self.config['assignment_type']].value(self.config['source_assg_dir'])

    @staticmethod
    def _write_default():
        """ Create a default AssignmentConfig file """
        json.dump(AssignmentConfig.default_assignment_config, open(paths.ASSIGNMENT_CONFIG, 'w'),
                  indent=4, sort_keys=True)

    def check_assignment_valid(self) -> Result:
        """ Check the configuration is valid """
        result = self.check_assignment_type()
        if result:
            result += self.check_source_assg_exists()
        if result:
            result += self.check_for_ci_file()
        return result

    def check_assignment_type(self) -> Result:
        """ Check that the assignment type listed has an existing implementation """
        assignment_types = [assg.name for assg in AssignmentType]

        if self.config['assignment_type'] in assignment_types:
            return Result(True, "Tournament is configured for: {}".format(self.config['assignment_type']))
        else:
            return Result(False, "ERROR: Assignment configuration has not been configured properly.\n"
                                 "       Please update {} with one of: {}"
                          .format(paths.ASSIGNMENT_CONFIG, assignment_types))

    def check_source_assg_exists(self) -> Result:
        """ Check that the path to the original source code is valid """
        source_assg_dir = self.config['source_assg_dir']
        if os.path.exists(source_assg_dir):
            return Result(True, "\tSource assignment is: {}".format(self.get_assignment().get_assignment_name()) +
                          "\n\tSource code dir: {}".format(source_assg_dir))
        else:
            return Result(False, "ERROR: Source assg dir {} does not exist".format(source_assg_dir))

    def check_for_ci_file(self) -> Result:
        """
        Assignments require a .gitlab-ci.yml file in order for a gitlab runner to validate and make submissions.
        Ensure it is present
        """
        gitlab_ci_file_path = self.config['source_assg_dir'] + "/.gitlab-ci.yml"
        if os.path.exists(gitlab_ci_file_path):
            return Result(True, "")
        else:
            return Result(False,
                          "ERROR: Expected gitlab_ci file not found at {}\n".format(gitlab_ci_file_path) +
                          "\n     Check docs/example_gitlab-ci.yml for an example of what this file should look like.")
