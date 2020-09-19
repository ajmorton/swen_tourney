# Config

Configuration for the tournament is found here.

## Config files
Contains the configuration data needed for the tournament to run properly. 
These files are also validated when the backend commands `check_config` and `start_tournament` are run to 
ensure proper tournament behaviour. If any of the validation checks fail then the tournament cannot start.


### assignment_config 
Provides the details of which assignment is to be used in the tournament.  

**Fields:**

- `assignment` the type of assignment the tournament is testing (ant_assignment, fuzz_assignment, etc). 
This assignment type is associated with an assignment configuration in the `assignment/` folder.  
- `source_assg_dir` a path to an original copy of the assignment to be used in the tournament. 
It is assumed that students will fork this code and add their test suites and PUTs to their own copies.

**Example file**

```json
{
    "assignment": "ant_assignment",
    "source_assg_dir": "/home/gitlab-runner/swen90006-a1-2019"
}
```

**Validation**  
Checks:

- the `assignment` type exists and has an implementation in `assignemnt`
- the provided `source_assg_dir` points to an existing copy of the assignment
- `source_assg_dir` contains a `.gitlab-ci.yml` file, which is needed for integration with the Gitlab Runner


### approved_submitters
Provides a list of submitters, identified by their gitlab usernames, that are allowed to make submissions to 
the tournament. Both the submitters unimelb usernames and student ids are provided as gitlab accounts can be named 
based on either of these values.

**Fields**  
`submission_deadline` the date and time at which submissions are closed
`submission_extensions_deadline` the date and time at which submission extensions are closed
`submitters` A list of approved submitters, identified by their gitlab username, and whether they are eligible for an extension

**Example file**

```json
{
    "submission_deadline": "2019-10-05 16:40:00",
    "submitters": ["student_a", "student_b", "student_c"]
}
```

**Validation**  
Checks that `approved_submitters.json` has been updated with non-default values, and that more than one 
submitter is present in the file.


### server_config
The details used by the results server to host the HTTP results webpage.

**Fields**  

- `host` the ip address the results server is hosted on. Always set to localhost
- `port` the port to host the HTTP server on

**Example file**

```json 
{
    "host": "127.0.0.1",
    "port": 8080
}
```

**Validation** 
None


### email_config
If the tournament raises an unexpected exception it will shutdown. 
When crash  report emailing is enabled then this configuration is used for the tournament to send an email 
via SMTP to provided recipients.

**Fields**  

- `sender` the email address to send tournament results from
- `password` the password of the sending email account
- `smtp_server` the smtp server to connect to in order to send the emails
- `port` the port to connect to the SMTP server on
- `crash_report_recipients` who to notify of tourney crashes

**Example file**  

```json
{
    "sender": "swen-tourney-noreply@unimelb.edu.au",
    "password": "email_password",
    "smtp_server": "smtp.unimelb.edu.au",
    "port": 587,
    "crash_report_recipients": ["recipient_1@mail.com", "recipient_2@mail.com"] 
}
```

**Validation** 
Checks that the provided `smtp_server` can be logged into using the provided `sender` username and `password`