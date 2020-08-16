# Setup

The tournament is designed to work with a Gitlab Shared Runner. 
Setup will require admin permissions for both the VPS that will host the tournament code and the Gitlab instance 
that will host student submissions.  
Setup of the VPS and Gitlab Runner only needs to be performed once and can be reused for subsequent assignments.

### Virtual Private Server (VPS)
The tournament code is expected to be run on a VPS on the unimelb network. Access to one can be requested from MSE IT.

By default all ports other than ssh (22) are closed by the network firewall. 
The tournament requires open ports for:

- the `alt-http` port (8080) preferably publicly visible outside of the university VPN, and
- the `smtp` port (465), if tournament crash report emailing is configured

This will require configuration both by MSE IT for the network firewall, and local configuration on the VPS 
itself using the `ufw` command.

Once completed the code in this repo can be copied to the `~gitlab-runner/` directory on the VPS.

### Gitlab
The tournament makes use of pipelines run via a [Gitlab Runner](https://docs.gitlab.com/runner/) to validate and 
submit student submissions. To set up the Gitlab Shared Runner:

1. [Install Gitlab Runner](https://docs.gitlab.com/runner/install/) on the VPS.

2. [Register a new Runner](https://docs.gitlab.com/runner/register/index.html) using the new `gitlab-runner` account.  
The gitlab instance and registration token can be found on the 
[Gitlab > Admin > Runners](https://gitlab.eng.unimelb.edu.au/admin/runners) page. The runner `executor` is `shell`. 
Make sure to attach a [tag](https://docs.gitlab.com/ee/ci/runners/#using-tags) to the runner to ensure only 
submissions to the tournament are executed by the runner.

3.  Make sure the runner is started.  
    Logged in as the `gitlab-runner` user (created in step 1) call `gitlab-runner run`. This will work without sudo permissions. 
    This starts the runner process and when a submission is made via gitlab traces will print such as:
    ```
    Checking for jobs... received                       job=87272 repo_url=https://gitlab.eng.unimelb.edu.au/ajmorton/swen90006-a1-2020.git runner=Mx1vPit9
    Job succeeded                                       duration=462.423825ms job=87272 project=9143 runner=Mx1vPit9
    ```
    This thread needs to continue running even after you end the ssh session on the VPS. 
    You can do this by pausing the process with  `ctrl+z` and then backgrounding it with `bg`
