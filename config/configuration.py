from config.exceptions import NoConfigDefined
from util.types import Result
from config.files.server_config import ServerConfig
from config.files.approved_submitters import ApprovedSubmitters
from config.files.email_config import EmailConfig
from config.files.assignment_config import AssignmentConfig


def check_configuration() -> Result:
    configs_valid = True
    traces = ""

    try:
        ServerConfig()

        # check assignment config is valid
        assignment_config = AssignmentConfig()
        assg_valid, assg_trace = assignment_config.check_non_default()
        configs_valid = configs_valid and assg_valid
        traces += assg_trace

        # check email config is valid
        email_config = EmailConfig()
        email_valid, email_trace = email_config.check_non_default()
        configs_valid = configs_valid and email_valid
        traces += email_trace

        # check approved submitters list is valid
        approved_submitters = ApprovedSubmitters()
        submitters_valid, submitters_trace = approved_submitters.check_non_default()
        configs_valid = configs_valid and submitters_valid
        traces += submitters_trace

        if configs_valid:
            traces += "Tournament configuration is valid"

    except NoConfigDefined as no_config_error:
        configs_valid = False
        traces = no_config_error.message

    return Result((configs_valid, traces))
