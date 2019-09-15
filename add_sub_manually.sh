#! /bin/bash

# add_sub_manually.sh
# Simulates the process performed by gitlab runner to make a submission
# To run `./add_sub_manually.sh <path_to_submission>`

# The tournament, and this script, determines the name of the submitted
# assignment by using `basename <path_to_submission>` and the name of 
# the submitter by using `basename $(dirname <path_to_submission>)` 
# e.g. ./add_sub_manually.sh /home/ajmorton/swen_tourney/example/student_a/example_assignment
# will determine assignment="example_assignment", submitter="student_a"

# note: When providing the submission path to add_sub_manually.sh make sure to remove the trailing `/`
# GOOD: ./add_sub_manually.sh /some/path/to/folder/student_a/example_assignment
# BAD:  ./add_sub_manually.sh /some/path/to/folder/student_a/example_assignment/

if [[ $# -eq 0 ]]; then
    echo "No submission provided"
    exit 1
fi

SUBMISSION=$1
SUBMITTER=$(basename $(dirname ${SUBMISSION}))

echo "Adding $SUBMITTER"
echo "checking elig"
python3 frontend.py check_eligibility ${SUBMISSION}
if [[ $? -ne 0 ]]; then
    echo "student not elig"
    exit 1
fi

echo "validating tests"
python3 frontend.py validate_tests ${SUBMISSION}
if [[ $? -ne 0 ]]; then
    echo "tests_not_val"
    exit 1
fi

echo "validating progs"
python3 frontend.py validate_progs ${SUBMISSION}
if [[ $? -ne 0 ]]; then
    echo "progs_not_val"
    exit 1
fi

echo "submitting"
python3 frontend.py submit ${SUBMISSION}
if [[ $? -ne 0 ]]; then
    echo "submit failed"
    exit 1
fi
