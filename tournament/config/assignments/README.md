# Assignment configs
The tournament can be configured to handle multiple types of assignments written in multiple languages and so there 
are a number of commands, such as running a test suite, that need to be performed differently for different assignment. 
The commands are all stored in an `assignment` class.

To create a configuration for a new assignment create a new class that extends from `abstract_assignment.py` and fill 
out all of the abstract methods.

### Considerations creating a new assignment
Make sure that in `prep_submission` that the original source code for the assignment is not overwritten by the 
submitters copy. For example is the `ant_assignment` the `programs/` contains `mutant-1`, `mutant-2`, `mutant-3` 
... `original`. Only mutant-1 through mutant-n are replaced, and `original` is not overwritten. This is to ensure 
that when `validate_tests` is run the submitters tests are actually checked against the original source code, and 
not a submitter modified version.

New assignments should aim for a generic extensible skeleton. For example `ant_assignment` has a folder called 
`programs` in which all mutants are stored, and a folder `tests` in which all tests are stored. The tournament 
code can then `ls` the folders to determine the number and name of the PUTs and test suites in the assignment. 

All assignments need to have a `.gitlab-ci.yml` file at the root level so that the Gitlab Runner knows to run a 
CI pipeline on the repos. This CI pipeline is how the code is validated and then submitted to the tournament. 
An example file can be [found here](../../../docs/example_gitlab-ci.yml) 