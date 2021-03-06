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
            raise NoConfigDefined(f"No assignment configuration file found at {paths.ASSIGNMENT_CONFIG} . "
                                  f"A default one has been created")
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
            return Result(True, f"Tournament is configured for: {self.config['assignment_type']}")
        else:
            return Result(False, f"ERROR: Assignment configuration has not been configured properly.\n"
                                 f"       Please update {paths.ASSIGNMENT_CONFIG} with one of: {assignment_types}")

    def check_source_assg_exists(self) -> Result:
        """ Check that the path to the original source code is valid """
        source_assg_dir = self.config['source_assg_dir']
        if os.path.exists(source_assg_dir):
            return Result(True, f"\tSource assignment is: {self.get_assignment().get_assignment_name()}" +
                          f"\n\tSource code dir: {source_assg_dir}")
        else:
            return Result(False, f"ERROR: Source assg dir {source_assg_dir} does not exist")

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
                          f"ERROR: Expected gitlab_ci file not found at {gitlab_ci_file_path}\n" +
                          "\n     Check docs/example_gitlab-ci.yml for an example of what this file should look like.")
