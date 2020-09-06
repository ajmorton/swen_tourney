# Common errors
Some common errors and their solutions are listed below:

* [Running with an older versions of python](#running-with-older-versions-of-python)
* [You are not allowed to download code from this project](#you-are-not-allowed-to-download-code-from-this-project)
* [getwd: not such file or directory](#getwd-no-such-file-or-directory)
* [Submitter is not on the approved submitters list](#submitter-is-not-on-the-approved-submitters-list)

## Errors

#### Running with older versions of python
The tournament code makes use of features in python that require 3.8.0 or later, and earlier versions of python 
will fail with varying syntax errors.  
You can verify your version of python using `python --version`, or make sure to use `python3.8` in place of `python`.

#### You are not allowed to download code from this project
```
remote: You are not allowed to download code from this project.
    fatal: unable to access 'https://gitlab-ci-token:xxxxxxxxxxxxxxxxxxxx@gitlab.eng.unimelb.edu.au/<username>/<assg_name>.git/': The requested URL returned error: 403
```
This error text arises when the @admin account on gitlab doesn't have the permissions to access a submitters 
private repository.  
This is due [Gitlab's build permissions policy](https://docs.gitlab.com/ee/user/project/new_ci_build_permissions_model.html#types-of-users) 
and requires that @admin is manually granted access to the repository in question. This can be performed as 
documented in the [assignment setup instructions](../README.md#Setup)

#### getwd: no such file or directory
```
Running with gitlab-runner 11.5.0 (3afdaba6)
  on swen90006-tourney-runner-mk2 K3qk8T7Z
ERROR: Preparation failed: Getwd: getwd: no such file or directory
Will be retried in 3s ...
ERROR: Preparation failed: Getwd: getwd: no such file or directory
Will be retried in 3s ...
ERROR: Preparation failed: Getwd: getwd: no such file or directory
Will be retried in 3s ...
ERROR: Job failed (system failure): Getwd: getwd: no such file or directory
```
This error typically arises when a prior Gitlab Shared Runner has not been stopped properly. Make sure that only 
the one gitlab runner is running on the VPS hosting the tournament code, using the gitlab-runner user account, 
checking with both `gitlab-runner list` and `ps -ef | grep -i gitlab`. The id of the gitlab runner should match 
the id provided in the traces (K3qk8T7Z in this case).  
The simplest solution is to make sure all gitlab runner processed are stopped, and then starting up 
a brand new gitlab runner.

#### Submitter is not on the approved submitters list
```
Checking submitter eligibility  
==================================
Submitter '<submitter_name>' is not on the approved submitters list.
```
The tournament checks whether a submitter is allowed to submit to the tournament by comparing against the data 
in approved_submitters.json. The Gitlab CI/CD pipeline determines the submitters username by extracting it from their 
git URL, e.g. `https://gitlab.eng.unimelb.edu.au/submitter_name/swen90006-a1-2020` will register the submitter name as 
`submitter_name`, and `submitter_name` needs to be present in approved_submitters.json.


