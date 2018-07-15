#!/bin/sh

# This is a basic script to do base setups on cloud instances, runs alongside cloud-init after an instance is provisioned
# TODO:
# 1) Disable cloud-init
# 2) remove root login
# 3) install pip
# 4) delete superfluous users
# 5) Fetch inventory file, then fetch ansible file as per inventory.cfg (maps a name to gist link)
# 6) Run ansible playbook against vm