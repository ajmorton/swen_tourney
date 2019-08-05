import reporting.results_server
import util.funcs

# The server is started in backend.py in a new thread via Popen.
# Due to how python namespacing works the new thread needs to run on a file at the rootdir of the project
# in order to have visibility on all packages. Hence, this file just calls start_server() in server.request_server
if __name__ == "__main__":
    util.funcs.assert_python_version(3, 5, 2)
    reporting.results_server.start_server()
