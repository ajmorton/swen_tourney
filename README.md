# swen_tourney

**SWEN Round-Robin Tournament Mk. 2**  
Tournament code to be used for SWEN subjects with bug/test suite tournaments.
Takes student submitted test suite(s) and program(s) under test (PUTs). All test suites are run against all PUTs in a round robin style, the results are then scored and ranked.

The tournament is designed to be integrated with a [Gitlab Shared Runner](https://docs.gitlab.com/ee/ci/runners/) so that students can make submissions and receive immediate feedback in an interactive manner.

### Contact
Andrew Morton ajmorton2@gmail.com

## How it works
The tournament is comprised of three 'threads'; A 'frontend' thread that validates submissions, a 'backend' thread that runs the submissions against each other, and a results thread that publishes results to a simple HTTP server.

See [How it works](docs/how_it_works.md) for further details.

## Setup
Instructions for setting up the VPS, Gitlab runner, and assignment code can be [found here](docs/setup_instructions.md)

## How to run
#### Dependencies
The tournaments only dependency is python 3.5.2 or later. The code is expected to be run on a VPS with no PyPi, apt, or other package managers and so should only depend on libraries from the python prelude.

#### Commands
Commands for the tournament are broken into [backend commands](docs/backend_commands.md) that manage the tournament, called via `python3 backend.py`, and [frontend commands](docs/frontend_commands.md) that are used to make submissions to the tournament, called via `python3 frontend.py`.

#### Typical workflow
A typical workflow for the tournament will look like

```sh
python3 backend.py check_config     # check the tournament is correctly configured
python3 backend.py start_tournament # submissions can now be made and tournament results can be seen on the 8080 port
	# students make submissions to the tournanent via the gitlab runner
	python3 frontend.py check_eligibility
	python3 frontend.py validate_tests
	python3 frontend.py validate_progs
	python3 frontend.py submit
python3 backend.py close_submissions     # close submissions, can be scheduled with the `at` command
python3 backend.py get_diffs             # generate diffs to be manually assessed
python3 backend.py rescore_invalid_progs # zero-score invalid PUTs
python3 backend.py shutdown              # shutdown the tournament
python3 backend.py clean                 # delete all submissions, config and traces
```

## Common errors
See [common errors](docs/common_errors.md)

## Extending the tournament to handle new assignments
See [config/assignments](tournament/config/assignments/README.md)

## TODO
- [ ] Updates to documentation
    - [ ] Use cases - "I want to X"
    - [ ] Document how to see what expected output looks like in Gitlab
- [ ] Organise tourney code and assignments into a single repo
	- [ ] add comment to assignments on how to adapt for a new assignment
	- [ ] Add comments on private repos and adding @admin to them with an expiry date
- [ ] Add "passed stage X" flags so that modification of .gitlab-ci.yml file doesn't allow invalid submissions to slip in
- [ ] Refactor
	- [ ] Replace dicts with typing.NamedTuples (python 3.6.2 required)
	- [ ] Keep removal of prior staged submissions?
- [ ] Add deadlines to approved_submitters, submitter_extensions
- [ ] Add a compile stage, break compilation logic out of verify_tests/verify_progs
- [ ] Add shutdown message to shutdown command e.g. "Restarting tournament. Back in 5"
- [ ] Update to traces?
- [ ] Readme per module
- [ ] Automated testing?
- [ ] Get a dedicated email account for the crash reports
- [ ] Add readme to ant_assignment with requirements
	- [ ] limit changes to gitlab-ci.yml
	- [ ] mandatory files and folders
- [ ] Code review
- [ ] Update the Gitlab Runner configuration? 
	- `shell` executor to `docker` executor?
	- Shared runner to Group runner?
- [ ] Simplify implementation (1400+ lines of code atm)
- [ ] Fix handling of server when port is already in use
    - [ ] Sometimes the results server thread is not being stopped and needs to be killed manually
- [ ] Subprocess timeouts don't work when the subprocess being called creates their own subprocesses and stdout/stderr are being sent to subprocess.PIPE
- [ ] Add checks to enforce each stage being run in order - students can't rerun submit without first running validate_progs etc
