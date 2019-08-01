from config.exceptions import NoConfigDefined
from config.files.server_config import ServerConfig
from config.files.approved_submitters import ApprovedSubmitters
from config.files.email_config import EmailConfig
from config.files.assignment_config import AssignmentConfig


def configuration_valid() -> bool:

    try:
        ServerConfig()

        # check assignment config is valid
        valid = AssignmentConfig().check_assignment_valid()

        if valid:
            # check email config is valid
            valid = EmailConfig().check_email_valid()

        if valid:
            # check approved submitters list is valid
            valid = ApprovedSubmitters().check_valid()

        if valid:
            # print server configs
            valid = ServerConfig().check_server_config()

        print("=================================")

        if valid:
            print("Tournament configuration is valid")
        else:
            print("Tournament has not been configured correctly. Please correct the above errors")

    except NoConfigDefined as no_config_error:
        print(no_config_error)
        return False

    return valid
