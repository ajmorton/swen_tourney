# Frontend commands
Commands sent to the frontend of the tournament are used to make student submissions to the tournament. These commands are expected to be run by a Gitlab Runner.

Commands are sent by calling `python3 frontend.py <command> <path_to_submission>`. `path_to_submission` is the path to a students submission. It expects the filepath structure `/absolute/path/to/submission/<submitter_name>/<assignment_name>` as the filepath is used by the tournament to extract the submitter name and assignment name. Gitlab Runners copy submissions to the server with this expected file path.

A list of available commands can be printed to screen by running `python3 frontend.py -h`. Further details on each command are provided below.

	python3 frontend.py --help
	
    check_eligibility   Check the submitter is eligible to submit to the tournament
    validate_tests      Validate the tests in a provided submission
    validate_progs      Validate the programs under test in a provided submission
    submit              Make a submission    

#### check_eligibility  
Checks that the submitter is on the `approved_submitters` list, and that the submitter has submitted the correct assignment code. On success the submission is moved to a pre_validation directory for assessment by later commands.

#### validate_tests
Runs after `check_eligibilty`. Checks the submission previously moved to the pre_validation directory by `check_eligibility`. Validates that the submitters test suite will not falsely report bugs in the original assignment code. If this check fails the submissions is removed from the pre_validation directory.		
#### validate_progs
Runs after `validate_tests`. Checks the submission previously moved to the pre_validation directory by `check_eligibility`. Validates that all of the submitters PUTs can be detected by a valid test suite. The submitters test suites are used to test their PUTs. If this check fails the submission is removed from the pre_vaidation directory.

#### submit
Runs after `validate_progs`. Moves the submission in the pre_validation directory to a staging directory for the tournament to process.