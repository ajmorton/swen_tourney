# how\_it\_works
Further details on the makeup of the tournament.

### Frontend
The frontend thread runs submissions through five stages.

 - `check_eligibility` which checks the submitter is allowed to make submissions to the tournament.
 - `compile` check that submitter's tests and PUTs compile
 - `validate_tests` that validates the submitter provided tests work correctly and don't return false positives
 - `validate_progs` that validates the submitter provided PUTs and proves that they can be detected by the submitters
 - `submit` which adds the new submission to the tournament

When properly integrated with a Gitlab Runner these stages will make up the CI pipeline for the assignment.

### Backend
When a submission is successfully made through the frontend thread above they are placed in a staging 
directory for processing in the backend thread. The backend thread listens for the addition of 
new submissions to this folder then takes new submissions, and runs them against all the previous submissions. 
The new submissions test suite is run against all other existing PUTs, and the submissions PUTs are run against 
all other existing test suites.

### Reporting
The scored and ranked submissions are published to an HTTP server, and are updated after every new submission.
