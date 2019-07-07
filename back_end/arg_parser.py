import argparse
import sys

# Formats the help message, removes some annoying text
class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


def create_parser(parser_list):
    parser = argparse.ArgumentParser(formatter_class=SubcommandHelpFormatter)
    subparsers = parser.add_subparsers(title='commands')

    # add the parser for the start_server command
    command_name = 'start_server'
    start_server_parser = subparsers.add_parser(
        command_name, help='Start the tournament back_end'
    )
    start_server_parser.set_defaults(type=command_name)
    parser_list[command_name] = start_server_parser

    # add the parser for the shutdown command
    command_name = 'shutdown'
    shutdown_parser = subparsers.add_parser(
        command_name, help='Shut down the tournament back_end'
    )
    shutdown_parser.set_defaults(type=command_name)
    parser_list[command_name] = shutdown_parser

    # add the parser for the send_report command
    command_name = 'report'
    report_parser = subparsers.add_parser(
        command_name, help='Get the results of the tournament. NOTE: This will take time to generate'
    )
    report_parser.add_argument('requester_email', help='Who to notify when the report is generated')
    report_parser.set_defaults(type=command_name)
    parser_list[command_name] = report_parser

    return parser


def print_help_text(parser_list, root_parser):
    print()

    # When argparse fails it throws only a SystemExit. To figure out which command failed look at sys.argv[1]
    command_name = sys.argv[1]

    if command_name in parser_list:
        parser_list[sys.argv[1]].print_help()
    else:
        root_parser.print_help()


def parse_args():
    sub_parser_list = dict()
    parser = create_parser(sub_parser_list)

    try:
        return parser.parse_args()

    except SystemExit:
        print_help_text(sub_parser_list, parser)
        exit(1)