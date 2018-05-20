#!/usr/bin/env python

import sys
import os
import yaml
from gomatic import *

GOCD_URL = os.environ["GOCD_URL"]
GOCD_USERNAME = os.environ["GOCD_USERNAME"]
GOCD_PASSWORD = os.environ["GOCD_PASSWORD"]
GOCD_TLS = False if "false" in os.environ["GOCD_TLS"] else True

DRY_RUN = True
if "DRY_RUN" in os.environ:
    if os.environ["DRY_RUN"] == "false":
        DRY_RUN = False

GOCD_TLS_VERIFY = True
if "GOCD_TLS_VERIFY" in os.environ:
    if os.environ["GOCD_TLS_VERIFY"] == "false":
        GOCD_TLS_VERIFY = False

configurator = GoCdConfigurator(HostRestClient(GOCD_URL, GOCD_USERNAME, GOCD_PASSWORD, GOCD_TLS, GOCD_TLS_VERIFY))

c = yaml.safe_load(open("gocd-config.yml").read())

CRs = configurator.ensure_replacement_of_config_repos()
configurator.remove_all_pipeline_groups()

security = configurator.ensure_replacement_of_security()
roles = security.ensure_replacement_of_roles()
authentication = security.ensure_replacement_of_auth_configs()
admins = security.ensure_admins()

all_users = []

for auth in c["server"]["auth"]:
    authentication.ensure_auth_config(auth["name"], auth["type"], auth["properties"])

for admin in c["server"]["users"]["admins"]:
    admins.add_user(name=admin)

for project in c["projects"]:
    for i in range(len(project["pipeline_groups"])):
        project["pipeline_groups"][i] = configurator.ensure_pipeline_group(project["pipeline_groups"][i])
    for group in project["groups"]:
        group["name"] = project["name"] + "-" + group["name"]
        if "permissions" not in group:
            permissions = []
        else:
            permissions = group["permissions"]

        permissions = set(permissions + ["view"])
        group["permissions"] = list(permissions)

        roles.ensure_role(
            name=group["name"],
            users=group["members"]
        )

        all_users = all_users + group["members"]


        for pg in project["pipeline_groups"]:
            pg.ensure_authorization().ensure_view().add_role("viewers")
            if "view" in permissions:
                pg.ensure_authorization().ensure_view().add_role(group["name"])

            if "operate" in permissions:
                pg.ensure_authorization().ensure_operate().add_role(group["name"])

            if "admin" in permissions:
                pg.ensure_authorization().ensure_admins().add_role(group["name"])


    # config-repos
    for repo in project["repos"]:
        CRs.ensure_config_repo(repo["url"], "yaml.config.plugin")

roles.ensure_role(
    name="viewers",
    users=set(all_users + c["server"]["users"]["viewers"])
)

configurator.save_updated_config(DRY_RUN, DRY_RUN)
