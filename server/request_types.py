from enum import Enum

from util.types import Submitter


class ServerResponse(str, Enum):
    ALIVE = 'ALIVE'
    REPORT_SUCCESS = 'REPORT_SUCCESS'
    SUBMISSION_SUCCESS = 'SUBMISSION_SUCCESS'
    SERVER_SHUTDOWN = 'SERVER_SHUTDOWN'


class RequestType(str, Enum):
    ALIVE = 'ALIVE'
    NONE = 'NONE'
    REPORT = 'REPORT'
    SUBMIT = 'SUBMIT'
    SHUTDOWN = 'SHUTDOWN'


class ServerRequest(dict):
    def __init__(self, request_type: RequestType, **kwargs):
        dict.__init__(self, request_type=request_type, **kwargs)
        self.request_type = request_type

    def get_request_type(self) -> RequestType:
        return self.request_type


class SubmissionRequest(ServerRequest):
    def __init__(self, submitter: Submitter):
        super().__init__(RequestType.SUBMIT, submitter=submitter)
        self.submitter = submitter


class ReportRequest(ServerRequest):
    def __init__(self, time: str):
        super().__init__(RequestType.REPORT, time=time)
        self.time = time


class ShutdownRequest(ServerRequest):
    def __init__(self):
        super().__init__(RequestType.SHUTDOWN)


class AliveRequest(ServerRequest):
    def __init__(self):
        super().__init__(RequestType.ALIVE)


def request_from_json(json):
    json.get("request_type")
    if "request_type" in json:
        if json["request_type"] == RequestType.ALIVE:
            return AliveRequest()
        if json["request_type"] == RequestType.SHUTDOWN:
            return ShutdownRequest()
        if json["request_type"] == RequestType.SUBMIT:
            return SubmissionRequest(json["submitter"])
        if json["request_type"] == RequestType.REPORT:
            return ReportRequest(json["time"])
    return ServerRequest(RequestType.NONE)
