"""
Configuration file validation performed on tournament startup
"""

from tournament.util import Result, Ansi
from .exceptions import NoConfigDefined
from .files import ApprovedSubmitters, AssignmentConfig, EmailConfig, ServerConfig, SubmitterExtensions


def configuration_valid() -> Result:
    """
    Check all configuration files on tournament startup. If any configuration file validation file fails return false.
    :return: Whether all configuration files are valid
    """

    try:
        ServerConfig()

        # check assignment config is valid
        result = AssignmentConfig().check_assignment_valid()
        if result:
            result += ApprovedSubmitters().check_valid()
        if result:
            result += ServerConfig().check_server_config()
        if result:
            result += SubmitterExtensions().check_valid()
        # if result:
        #    result += EmailConfig().check_email_valid()

    except NoConfigDefined as no_config_error:
        result = Result(False, no_config_error.message)

    result += "================================="
    if result:
        result += f"{Ansi.GREEN}Tournament configuration is valid{Ansi.END}"
    else:
        result += f"{Ansi.RED}Tournament has not been configured correctly. Please correct the above errors{Ansi.END}"

    return result
