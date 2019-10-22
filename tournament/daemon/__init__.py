"""
Daemon process that waits for submissions to be copied into the paths.STAGED_DIR folder and processes them by
order of submission
"""

from .fs_queue import queue_submission
from .main import main, shutdown, make_report_request, is_alive, start
