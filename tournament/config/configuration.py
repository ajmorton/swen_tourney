"""
Configuration file validation performed on tournament startup
"""

from tournament.config.exceptions import NoConfigDefined
from tournament.config.files import ApprovedSubmitters, AssignmentConfig, ServerConfig, SubmitterExtensions


def configuration_valid() -> bool:
    """
    Check all configuration files on tournament startup. If any configuration file validation file fails return false.
    :return: Whether all configuration files are valid
    """

    try:
        ServerConfig()

        # check assignment config is valid
        valid = AssignmentConfig().check_assignment_valid() \
            and ApprovedSubmitters().check_valid() \
            and ServerConfig().check_server_config() \
            and SubmitterExtensions().check_valid()
        # and EmailConfig().check_email_valid()

    except NoConfigDefined as no_config_error:
        print(no_config_error.message)
        valid = False

    print("=================================")
    if valid:
        print("Tournament configuration is valid")
    else:
        print("Tournament has not been configured correctly. Please correct the above errors")

    return valid
