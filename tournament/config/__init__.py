"""
Configuration file validation performed on tournament startup
"""

from .files import ApprovedSubmitters, AssignmentConfig, EmailConfig, ServerConfig, SubmitterExtensions
from .exceptions import NoConfigDefined
from tournament.util import Result


def configuration_valid() -> Result:
    """
    Check all configuration files on tournament startup. If any configuration file validation file fails return false.
    :return: Whether all configuration files are valid
    """

    try:
        ServerConfig()

        # check assignment config is valid
        result = AssignmentConfig().check_assignment_valid() + \
            ApprovedSubmitters().check_valid() + \
            ServerConfig().check_server_config() + \
            SubmitterExtensions().check_valid()
        # EmailConfig().check_email_valid()

    except NoConfigDefined as no_config_error:
        result = Result(False, no_config_error.message)

    result += "================================="
    if result:
        result += "Tournament configuration is valid"
    else:
        result += "Tournament has not been configured correctly. Please correct the above errors"

    return result
