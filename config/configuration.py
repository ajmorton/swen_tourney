from config.assignments.ant.AntAssignment import AntAssignment
from config.exceptions import NoConfigDefined
from tournament.types.basetypes import Result
from config.files.server_config import ServerConfig
from config.files.approved_submitters import ApprovedSubmitters
from config.files.email_config import EmailConfig

# Which assignment the tournament is configured for
# TODO how to hotswap assignment imports?
assignment = AntAssignment()


def check_configuration() -> Result:
    configs_valid = True
    traces = ""

    try:
        ServerConfig()

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
