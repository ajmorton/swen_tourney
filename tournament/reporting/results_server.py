"""
Results of the tournament are written to an HTTP server.
The server delivers a static page with a ranked table of submitters
"""

import os
import subprocess
import threading
import time
import traceback
from datetime import datetime
from http import HTTPStatus, server
from socketserver import ThreadingMixIn

from tournament.config import AssignmentConfig, ServerConfig
from tournament.flags import get_flag, TourneyFlag
from tournament.processing import TourneySnapshot
from tournament.util import Result
from tournament.util import format as fmt, paths
from tournament.util import print_tourney_trace, print_tourney_error


class ThreadedHTTPServer(ThreadingMixIn, server.HTTPServer):
    """ Default server.HTTPServer, but uses ThreadingMixIn to be able to handle multiple HTTP requests in parallel """


class TourneyResultsHandler(server.SimpleHTTPRequestHandler):
    """ HTTP request handler that returns a ranked table of submitter results """

    def do_GET(self):
        """ Handle GET requests to the server """

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        snapshot = TourneySnapshot(snapshot_file=paths.RESULTS_FILE)
        report_date = snapshot.date()

        html = '<!DOCTYPE html><html><body>' \
               '<h1>Results as of ' + report_date.strftime(fmt.DATETIME_TRACE_STRING) + '</h1>' + \
               tournament_processing_details(snapshot) + \
               _html_table_from_results(snapshot) + \
               '</body></html>'

        self.wfile.write(bytes(html, 'utf-8'))

    def do_HEAD(self):
        self.do_GET()

    # noinspection PyPep8Naming
    def do_POST(self):  # pylint: disable=invalid-name
        """ Don't accept POST requests """
        self.send_error(HTTPStatus.NOT_IMPLEMENTED, "POST requests are not accepted")

    def list_directory(self, path):
        # stubbed
        return None

    def log_message(self, log_format, *args):  # pylint: disable=arguments-differ,unused-argument
        with open(paths.RESULTS_SERVER_TRACE_FILE, 'a') as file:
            file.write("{} - - [{}] {}\n".format(self.address_string(), self.log_date_time_string(), *args))


def tournament_processing_details(snapshot: TourneySnapshot) -> str:
    """ Return a string with submissions still to process and the current submission processing duration """
    queued_submissions = len([file for file in os.listdir(paths.STAGING_DIR) if not file.startswith(".")])
    time_to_process_last_submission = snapshot.time_to_process_last_submission()

    return f"There are {queued_submissions} submissions awaiting processing.\n" + \
           f"The most recent submission took {time_to_process_last_submission} seconds to process"


def _html_table_from_results(snapshot: TourneySnapshot) -> str:
    """
    Convert the tournament snapshot to a ranked table of submitter results
    :param snapshot: the tournament snapshot data
    :return: a string of an HTML table with submitter results
    """

    num_submitters = snapshot.num_submitters()
    assg = AssignmentConfig().get_assignment()
    num_tests = 0 if num_submitters == 0 else (num_submitters - 1) * len(assg.get_test_list())
    num_progs = 0 if num_submitters == 0 else (num_submitters - 1) * len(assg.get_programs_list())

    tests_header = f"<table><tr><th>Bugs detected (out of {num_progs})</th></tr>" + \
                   f"<tr><td>{str(sorted(assg.get_test_list()))}</tr></td></table>"
    progs_header = f"<table><tr><th>Tests evaded (out of {num_tests})</th></tr>" + \
                   f"<tr><td>{str(sorted(assg.get_programs_list()))}</tr></td></table>"

    table = '<table style="width:100%" align="center">' + \
        _table_header("Rank", "Name", "Date of submission", tests_header, progs_header)

    table += _table_body_from_results(snapshot)

    return table


def _table_body_from_results(snapshot: TourneySnapshot) -> str:
    """ Generate the body of the results table from the tournament results """
    table = ''
    results = snapshot.results()

    table_data = {}
    for submitter in results:
        score = float(results[submitter]['normalised_test_score']) + float(results[submitter]['normalised_prog_score'])

        table_data[submitter] = {'latest_processed_submission': results[submitter]['latest_submission_date'],
                                 'score': score,
                                 'progs': results[submitter]['progs'],
                                 'tests': results[submitter]['tests'],
                                 }

    rank = 0
    prev_score = -1

    # print results from best score to worst
    for submitter, sub_data in sorted(table_data.items(), key=lambda item: item[1]['score'], reverse=True):
        if sub_data['latest_processed_submission'] is None:
            table += _table_row("-", submitter, "No submission", "N/A", "N/A")
        else:
            latest_submission_date = datetime.strptime(sub_data['latest_processed_submission'],
                                                       fmt.DATETIME_TRACE_STRING)

            prog_scores = [sub_data['progs'][prog] for prog in sorted(sub_data['progs'])]
            test_scores = [sub_data['tests'][test] for test in sorted(sub_data['tests'])]

            latest_submission_date = latest_submission_date.strftime(fmt.DATETIME_TRACE_STRING)

            if prev_score != sub_data['score']:
                rank += 1
                prev_score = sub_data['score']
            table += _table_row(rank, submitter, latest_submission_date, test_scores, prog_scores)

    table += '</table>'

    return table


def _table_header(*args) -> str:
    """ Return an HTML table header string. The size of the row depends on the number of values in *args """
    row = '<tr>'
    for col in args:
        row += '<th align="center">' + str(col) + '</th>'
    row += '<tr>'
    return row


def _table_row(*args) -> str:
    """ Return an HTML table row string. The size of the row depends on the number of values in *args """
    row = '<tr>'
    for col in args:
        row += '<td align="center">' + str(col) + '</td>'
    row += '<tr>'
    return row


def _server_assassin(httpd: ThreadedHTTPServer):
    """
    An assassin thread that checks for the removal of the tournament alive flag.
    When it get removed kill the server thread
    :param httpd: the HTTP server to kill
    """
    while get_flag(TourneyFlag.ALIVE):
        time.sleep(5)

    httpd.shutdown()


def main():
    """ Run the results server thread """

    try:
        time.sleep(5)
        print_tourney_trace("Starting the results server")
        if not os.path.exists(paths.RESULTS_FILE):
            TourneySnapshot(report_time=datetime.now()).write_snapshot()
        server_config = ServerConfig()
        server_address = ('', server_config.port())
        httpd = ThreadedHTTPServer(server_address, TourneyResultsHandler)
        threading.Thread(target=_server_assassin, args=[httpd], daemon=True).start()
        httpd.serve_forever()
        print_tourney_trace("Shutting down the results server")
    except Exception as exception:  # pylint: disable=broad-except
        print_tourney_error("Exception caught while running Results Server")
        print_tourney_error(str(exception))
        print_tourney_error(traceback.format_exc())
        # wait 5 minutes to ensure the port is freed
        time.sleep(300)
        main()


def start_server() -> Result:
    """ Start the results server in its own thread """
    subprocess.Popen("python3.8 -m tournament.reporting.results_server", cwd=paths.ROOT_DIR, shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Result(True, f"Results server starting. Listening on port {ServerConfig().port()}")


if __name__ == '__main__':
    main()
