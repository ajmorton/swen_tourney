
from enum import Enum
from config.assignments.AbstractAssignment import AbstractAssignment
from config.assignments.ant.AntAssignment import AntAssignment
import json
import os
from util import paths
from config.exceptions import NoConfigDefined


class AssignmentType(Enum):
    ant_assignment = AntAssignment()


class AssignmentConfig:

    def __init__(self):
        if not os.path.exists(paths.ASSIGNMENT_CONFIG):
            AssignmentConfig.write_default()
            raise NoConfigDefined("No assignment configuration file found at {}. A default one has been created"
                                  .format(paths.ASSIGNMENT_CONFIG))
        else:
            self.assignment = json.load(open(paths.ASSIGNMENT_CONFIG, 'r'))

    def get_assignment(self) -> AbstractAssignment:
        return AssignmentType[self.assignment].value

    @staticmethod
    def write_default():
        json.dump("enter_assignment_type_here", open(paths.ASSIGNMENT_CONFIG, 'w'), indent=4)

    def check_assignment_valid(self) -> bool:
        valid = self.check_assignment_type()

        if valid:
            valid = self.check_source_assg_exists()

        print()
        return valid

    def check_assignment_type(self) -> bool:
        assignment_types = [assg.name for assg in AssignmentType]

        if self.assignment in assignment_types:
            print("Tournament is configured for: {}".format(self.assignment))
            return True
        else:
            print("ERROR: Assignment configuration has not been configured properly.\n"
                  "       Please update {} with one of: {}"
                  .format(paths.ASSIGNMENT_CONFIG, assignment_types))
            return False

    def check_source_assg_exists(self) -> bool:
        source_assg_dir = self.get_assignment().get_source_assg_dir()
        if os.path.exists(source_assg_dir):
            print("\tSource assg dir exists")
            return True
        else:
            print("ERROR: Source assg dir {} does not exist".format(source_assg_dir))
            return False


