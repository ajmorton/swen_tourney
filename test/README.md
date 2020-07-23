# Testing

`simulate_tournament.py` can be used to simulate a tournament by replaying a batch of submissions inside 
the `submissions` folder. The script will then chronologically order all commits across all submissions and submit 
them to the tournament in order.  

## Setup
After correctly configuring the tournament place the submissions to replay inside the `submissions` folder.
The folder structure of each submission should be `<submitter>/<assignment>`, where `submitter` is the name 
of a submitter who is eligible to participate in the tournament, and `assignment` is the assignment 
that the tournament is configured for.

For example if the tournament is configured to run the `swen90006-a2-2019` assignment and `approved_sunmitters.json` 
contains submitters `student_a`, `student_b`, and `student_c` then the folder structure should look like:

```
test
├── simulate_tournament.py
├── README.md
└── submissions
    ├── submission_a
    │   └── swen90006-a2-2019/
    ├── submission_b
    │   └── swen90006-a2-2019/
    └── submission_c
        └── swen90006-a2-2019/

```

## Run
**_Do not run this script when an actual tournament is underway. 
The tournament does not discriminate between submissions made via Gitlab Runner and this script and the test submissions will overwrite previous, valid, submissions.  
If you are running this script either perform it in a fresh clone of `swen_tourney` or make sure to backup the `state` folder first_**

To replay the tournament run `python3.8 -m test.simulate_tournament` from the root of the repository.

