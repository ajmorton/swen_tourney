# swen-tourney

**SWEN Round-Robin Tournament Mk. 2**  
Tournament code to be used for SWEN subjects with bug/test suite tournaments.

## TASKS
- Base structure
    - Tournament server
    - Request API
- Message structure
    - JSON, what requests can be made
- Emailer
- Assignment code integration
    - Example assignments
    - Dynamic compilation of example code
    - Assignment code folder structure (to be constant across all assignments)
- Gitlab CI integration
    - Runner setup
    - Validation Traces
- Documentation
    - Gitlab CI Setup Instructions
    - Program Control flow

## TODO
- Plan for
    - How to handle traces
    - How to handle crashes robustly
        - Save state to disk and allow for tournament to resume?
    - Performance under load
        - Related to dynamic compilation above
        - Test submissions on reception or test all submissions at once?
        - Rate limit student submissions?