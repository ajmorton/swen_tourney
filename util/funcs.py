import sys


def assert_python_version(major: int, minor: int, micro: int):
    py_version = sys.version_info
    if py_version.major != major or py_version.minor != minor or py_version.micro != micro:
        print("ERROR: You are currently using Python {}.{}.{}".format(
            py_version.major, py_version.minor, py_version.micro)
        )
        print("Please run this program using Python {}.{}.{}".format(major, minor, micro))
        exit(1)
