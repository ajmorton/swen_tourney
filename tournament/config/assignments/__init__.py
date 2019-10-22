"""
Assignment configurations that can be used by the tournament
AbstractAssignment is an interface that each implementation must inherit from
"""
from .abstract_assignment import AbstractAssignment
from .ant_assignment import AntAssignment
from .fuzz_assignment import FuzzAssignment
