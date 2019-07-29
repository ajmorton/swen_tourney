
from enum import Enum
from config.assignments.DefaultAssignment import DefaultAssignment
from config.assignments.AbstractAssignment import AbstractAssignment
from config.assignments.ant.AntAssignment import AntAssignment
import json
import os
from util import paths
from util.types import Result
from config.exceptions import NoConfigDefined


class AssignmentType(Enum):
    default = DefaultAssignment()
    ant_assignment = AntAssignment()


class AssignmentConfig:

    default_assignment = AssignmentType.default.name

    def __init__(self):
        if not os.path.exists(paths.ASSIGNMENT_CONFIG):
            AssignmentConfig.write_default()
            raise NoConfigDefined("No email configuration file found at {}. A default one has been created"
                                  .format(paths.ASSIGNMENT_CONFIG))
        else:
            self.assignment = json.load(open(paths.ASSIGNMENT_CONFIG, 'r'))

    def get_assignment(self) -> AbstractAssignment:
        return AssignmentType[self.assignment].value

    @staticmethod
    def write_default():
        json.dump(AssignmentConfig.default_assignment, open(paths.ASSIGNMENT_CONFIG, 'w'), indent=4)

    @staticmethod
    def write_assg_type(assg_type: str) -> Result:
        json.dump(assg_type, open(paths.ASSIGNMENT_CONFIG, 'w'), indent=4)
        return Result((True, "{} assignment configuration set".format(assg_type)))

    def check_non_default(self) -> Result:
        if self.assignment != AssignmentConfig.default_assignment:
            return Result((True, "Tournament is configured for: {}\n".format(self.assignment)))
        else:
            return Result((False, "ERROR: Assignment configuration has not been configured.\n"
                                  "       Please update {} with the correct details\n".format(paths.ASSIGNMENT_CONFIG)))



