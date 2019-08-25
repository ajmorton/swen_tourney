import http.server
from http import HTTPStatus
from datetime import datetime
from util import format as fmt
from tournament.state.tourney_snapshot import TourneySnapshot
from util import paths
from config.configuration import AssignmentConfig, ServerConfig
from daemon import flags
import threading
import time
import subprocess
from util.funcs import print_tourney_trace, print_tourney_error
from util.types import Result
import os


class TourneyResultsHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        """
        Handle GET requests to the server by
        :return:
        """

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        snapshot = TourneySnapshot(snapshot_file=paths.RESULTS_FILE)
        report_date = snapshot.date()

        html = '<!DOCTYPE html><html><body>' \
               '<h1>Results as of ' + report_date.strftime(fmt.datetime_trace_string) + '</h1>' + \
               tournament_processing_details(snapshot) + \
               html_table_from_results(snapshot) + \
               '</body></html>'

        self.wfile.write(bytes(html, 'utf-8'))

    def log_message(self, log_format, *args):
        return


def tournament_processing_details(snapshot: TourneySnapshot) -> str:
    queued_submissions = len(os.listdir(paths.STAGING_DIR))
    time_to_process_last_submission = snapshot.time_to_process_last_submission()

    return "There are {} submissions awaiting processing.\n".format(queued_submissions) + \
           "The most recent submission took {} seconds to process".format(time_to_process_last_submission)


def html_table_from_results(snapshot: TourneySnapshot) -> str:

    results = snapshot.results()
    num_submitters = snapshot.num_submitters()
    assg = AssignmentConfig().get_assignment()
    num_tests = 0 if num_submitters == 0 else (num_submitters - 1) * len(assg.get_test_list())
    num_progs = 0 if num_submitters == 0 else (num_submitters - 1) * len(assg.get_programs_list())

    table_data = {}
    for submitter in results:
        score = float(results[submitter]['normalised_test_score']) + float(results[submitter]['normalised_prog_score'])

        table_data[submitter] = {'latest_processed_submission': results[submitter]['latest_submission_date'],
                                 'score': score,
                                 'progs': results[submitter]['progs'],
                                 'tests': results[submitter]['tests'],
                                 }

    tests_header = "<table><tr><th>Bugs detected (out of {})</th></tr>".format(num_progs) + \
                   "<tr><td>" + str(sorted(assg.get_test_list())) + "</tr></td></table>"
    progs_header = "<table><tr><th>Tests evaded (out of {})</th></tr>".format(num_tests) + \
                   "<tr><td>" + str(sorted(assg.get_programs_list())) + "</tr></td></table>"

    table = '<table style="width:100%" align="center">' + \
        table_header("Rank", "Name", "Date of submission", tests_header, progs_header)

    rank = 0
    prev_score = -1

    # print results from best score to worst
    for submitter, sub_data in sorted(table_data.items(), key=lambda item: item[1]['score'], reverse=True):
        if sub_data['latest_processed_submission'] is None:
            table += table_row("-", submitter, "No submission", "N/A", "N/A")
        else:
            latest_submission_date = datetime.strptime(sub_data['latest_processed_submission'],
                                                       fmt.datetime_trace_string)

            prog_scores = [sub_data['progs'][prog] for prog in sorted(sub_data['progs'])]
            test_scores = [sub_data['tests'][test] for test in sorted(sub_data['tests'])]

            latest_submission_date = latest_submission_date.strftime(fmt.datetime_trace_string)

            if prev_score != sub_data['score']:
                rank += 1
                prev_score = sub_data['score']
            table += table_row(rank, submitter, latest_submission_date, test_scores, prog_scores)

    table += '</table>'

    return table


def table_header(*args) -> str:
    row = '<tr>'
    for col in args:
        row += '<th align="center">' + str(col) + '</th>'
    row += '<tr>'
    return row


def table_row(*args) -> str:
    row = '<tr>'
    for col in args:
        row += '<td align="center">' + str(col) + '</td>'
    row += '<tr>'
    return row


def server_assassin(httpd: http.server.HTTPServer):
    """
    Checks for the removal of the tournament alive flag. When it get removed kill the server
    :param httpd: the HTTP server to kill
    :return:
    """
    while flags.get_flag(flags.Flag.ALIVE):
        time.sleep(5)

    httpd.shutdown()


def main():

    try:
        if not os.path.exists(paths.RESULTS_FILE):
            TourneySnapshot(report_time=datetime.now()).write_snapshot()

        server_config = ServerConfig()
        server_address = ('', server_config.port())
        httpd = http.server.HTTPServer(server_address, TourneyResultsHandler)
        threading.Thread(target=server_assassin, args=[httpd], daemon=True).start()
        httpd.serve_forever()
        print_tourney_trace("Shutting down the results server")
    except Exception as e:
        print_tourney_error("Exception caught while running Results Server")
        print_tourney_error(str(e))
        import traceback
        print_tourney_error(traceback.format_exc())
        # wait 5 minutes to ensure the port is freed
        time.sleep(300)
        main()


def start_server():
    subprocess.Popen("python3 -m reporting.results_server", cwd=paths.ROOT_DIR, shell=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Result((True, "Results server starting. Listening on port {}".format(ServerConfig().port())))


if __name__ == '__main__':
    main()
