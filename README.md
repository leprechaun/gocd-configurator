# gocd-configurator

A simple declarative YAML config to manage gocd.

*NO this isn't meant to manage pipelines*

## Problem statement

I'd rather not be editing `cruise.xml`, ever, because it's sad.

I don't want to check it into git because it's still pretty coupled w/ the GoCD installation.

I'd like to have my GoCD pipeline (config repos) managed through git itself, as simple list.

I'd like to have my AuthZ and AuthN clearly visible, through git. And even manageable!

## Solution

*Tada!*

This repo lets you write a structured YAML document, which expresses most of my own needs for `cruise.xml`.

```
server:
  auth: # auth configs
    - name: passwd
      type: cd.go.authentication.passwordfile
      properties: # passed straight to gomatic
        PasswordFilePath: /go-working-dir/config/passwd
  users: # Global users that can either view, or admin GoCD
    viewers:
      - some-user
    admins:
      - a-power-user-that-is-trusted

projects:
  - name: name-of-my-project
    # Each of these will result in a config repo
    repos: 
      - url: https://example-git-host/path/to/repo.git
    # These pipeline groups are just here for AuthN.
    # If your configrepos use different pipeline-groups, there isn't much we can do here. yet ...
    pipeline_groups:
      - my-projects-pipeline-group
    # Each of the groups below will grant privileges to the pipeline-groups above
    groups:
      # Each group will result in group called "${project_name}-${group_name}"
      # with the permissions attributed. `view` is granted by default.
      - name: business-analysts
        members:
          - mr-business-analyst
      - name: admins
        permissions:
          - operate
          - admin
        members:
          - mrs-administrator
```

In addition to the projet specific groups, I believe everyone should see everything going on. Therefore, all users will have 'view' on all pipeline groups.
