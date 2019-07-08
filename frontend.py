import cli.arg_parser as parser
import tournament.main as tournament


def main():
    """
    Parse and process commands
    """
    event = parser.parse_frontend_args()
    event = vars(event)

    event_type = event['type']

    if event_type == "validate_tests":
        success = tournament.validate_tests(event['dir'])
    elif event_type == "validate_puts":
        success = tournament.validate_programs_under_test(event['dir'])
    elif event_type == "submit":
        submission_dir = event["dir"]
        submitter = submission_dir.split("/")[-1]
        success = tournament.submit(submitter, submission_dir)
    else:
        success = False

    if success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()