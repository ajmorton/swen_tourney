"""
Which assignment the tournament is configured for and validation of these details
"""

import json
import os
from enum import Enum

from config.assignments.abstract_assignment import AbstractAssignment
from config.assignments.ant_assignment import AntAssignment
from config.exceptions import NoConfigDefined
from util import paths


class AssignmentType(Enum):
    """ The available assignment types to choose from """
    ant_assignment = AntAssignment


class AssignmentConfig:
    """ Contains configuration details for which tournament the assignment is set up for. """

    default_assignment_config = {
        'assignment': "enter_assignment_type_here",
        'source_assg_dir': "/absolute/path/to/assignment"
    }

    def __init__(self):
        if not os.path.exists(paths.ASSIGNMENT_CONFIG):
            AssignmentConfig.write_default()
            raise NoConfigDefined("No assignment configuration file found at {}. A default one has been created"
                                  .format(paths.ASSIGNMENT_CONFIG))
        else:
            self.config = json.load(open(paths.ASSIGNMENT_CONFIG, 'r'))

    def get_assignment(self) -> AbstractAssignment:
        """ Get which assignment the tournament has been configured for """
        return AssignmentType[self.config['assignment']].value(self.config['source_assg_dir'])

    @staticmethod
    def write_default():
        """ Create a default AssignmentConfig file """
        json.dump(AssignmentConfig.default_assignment_config, open(paths.ASSIGNMENT_CONFIG, 'w')
                  , indent=4, sort_keys=True)

    def check_assignment_valid(self) -> bool:
        """ Check the configuration is valid """
        valid = self.check_assignment_type()

        if valid:
            valid = self.check_source_assg_exists()

        print()
        return valid

    def check_assignment_type(self) -> bool:
        """ Check that the assignment type listed has an existing implementation """
        assignment_types = [assg.name for assg in AssignmentType]

        if self.config['assignment'] in assignment_types:
            print("Tournament is configured for: {}".format(self.config['assignment']))
            return True
        else:
            print("ERROR: Assignment configuration has not been configured properly.\n"
                  "       Please update {} with one of: {}"
                  .format(paths.ASSIGNMENT_CONFIG, assignment_types))
            return False

    def check_source_assg_exists(self) -> bool:
        """ Check that the path to the original source code is valid """
        source_assg_dir = self.config['source_assg_dir']
        if os.path.exists(source_assg_dir):
            print("\tSource assignment is: {}".format(AntAssignment(source_assg_dir).get_assignment_name()))
            print("\tSource code dir: {}".format(source_assg_dir))
            return True
        else:
            print("ERROR: Source assg dir {} does not exist".format(source_assg_dir))
            return False
