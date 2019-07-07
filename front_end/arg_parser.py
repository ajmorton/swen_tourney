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

    # common parser for parsing the submission directory's path
    directory_parser = argparse.ArgumentParser(add_help=False)
    directory_parser.add_argument('dir', help="The directory of the submission to test")

    # add the parser for the validate_tests command
    command_name = 'validate_tests'
    val_test_parser = subparsers.add_parser(
        command_name, help='Validate the tests in a provided submission', parents=[directory_parser]
    )
    val_test_parser.set_defaults(type=command_name)
    parser_list[command_name] = val_test_parser

    # add the parser for the process_submission command
    command_name = 'validate_mutants'
    val_mut_parser = subparsers.add_parser(
        command_name, help='Validate the mutants in a provided submission', parents=[directory_parser]
    )
    val_mut_parser.set_defaults(type=command_name)
    parser_list[command_name] = val_mut_parser

    # add the parser for the submit command
    command_name = 'submit'
    submit_parser = subparsers.add_parser(
        command_name, help='Make a submission', parents=[directory_parser]
    )
    submit_parser.set_defaults(type=command_name)
    parser_list[command_name] = submit_parser

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