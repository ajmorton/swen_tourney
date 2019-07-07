import front_end.arg_parser as parse
import tournament.main as tournament


def main():
    """
    Parse and process commands
    """
    event = parse.parse_args()
    event = vars(event)

    event_type = event['type']

    if event_type == "validate_tests":
        success = tournament.validate_tests(event['dir'])
    elif event_type == "validate_mutants":
        success = tournament.validate_mutants(event['dir'])
    elif event_type == "submit":
        success = tournament.submit(event)
    else:
        success = False

    if success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
