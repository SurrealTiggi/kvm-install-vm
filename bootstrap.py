#!/usr/env/python2

'''
This is a basic script to do base setups on cloud instances, runs alongside cloud-init after an instance is provisioned
TODO:
1) Fetch your personal inventory.yml file DONE
2) Set up local inventory for ansible
3) Run ansible playbook against vm
'''

# Imports
import sys
import logging
import os
from os.path import expanduser
import requests
import re
import yaml
import argparse
from yaml import load, dump

# Static variables
FORMAT = '%(asctime)s || %(levelname) || [%(filename)s:%(lineno)s - %(funcName)20s() ] : %(message)s'
if os.name == 'nt':
    LOGFILE = str(os.getcwd() + '\\bootstrap.log')
    HOME = str(expanduser("~") + '\\')
else:
    LOGFILE = str(os.getcwd() + '/bootstrap.log')
    HOME = str(expanduser("~") + '/')

# Colors for readability
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def fetchInventory(url):
    try:
        r = requests.get(str(url))
        return r
    except Exception as e:
        log.error('Failed to fetch given url << ' + str(url) + ' >>: ' + str(e))
        return False

def validateInventory():
    log.debug("Validating inventory...")

    try:
        # This will load the inventory file into an easily queryable object that we can loop through
        with open(HOME + 'inventory.yml', 'r') as myfile:
            myinventory = myfile.read()
        inv = yaml.load(myinventory)

        '''
        Cases as follows:
        1) Ensure /etc/ansible/hosts is complete (INVENTORY.YML IS GOSPEL)
        2) If git[enabled] = true -> Book out the entire project and ansible-playbook ansible_scripts/<host>
        3) If git[enabled] = false -> Grab defaults.yml
        4) Get singular playbook -> Download the relevant playbook and ansible-playbook ansible_scripts/<host>
        TODO: switch case tutorial
        https://jaxenter.com/implement-switch-case-statement-python-138315.html
        '''

        for key in inv.keys():
            if key == 'git':
                # Check
                pass
            elif key == 'config':
                pass


    except Exception as e:
        log.error('Failed to process inventory.yml file: ' + str(e))
        print(Colors.FAIL + 'Unable to continue as your inventory file is un-readable. Please check it and re-run this script.')
        sys.exit()


def runAnsible(instance):
    log.debug('Running with ' + instance)

def promptUser():

    answer = input(Colors.OKBLUE + 'Please specify the full URL location of your personal inventory.yml (eg. https://gist.githubusercontent.com/someuser/hash/raw/anotherhash/defaults.yml):\n\t')
    inventory = fetchInventory(answer)

    if not inventory:
        print(Colors.WARNING + 'Invalid URL given. Please retry...')
        promptUser()
    elif inventory.status_code != 200:
        print(Colors.WARNING + 'Non-existant URL given. Please retry...')
        promptUser()
    else:
        print(Colors.OKGREEN + "Valid URL given, saving inventory")
        open(HOME + 'inventory.yml', 'wb').write(inventory.content)
    
def main(instance):
    '''
    Bootstrapping utility for cloud-init VMs, works as follows:
    * Checks if inventory.yml exists in current user's $HOME
    * If not, requests location to fetch it (a URL by default)
    * Once the file is present, parse it, validate local inventory, then run ansible-playbooks
    * When finished, delete inventory.yml. That way, the external source remains gospel.
    '''
    log.debug("Starting bootstrap...")
    if not os.path.isfile(HOME + 'inventory.yml'):
        promptUser()
        validateInventory()
        runAnsible(instance)
    else:
        validateInventory()
        runAnsible(instance)

if __name__ == '__main__':
    logging.basicConfig(format=FORMAT, filename=LOGFILE, level=os.environ.get("LOGLEVEL", "DEBUG"))
    log = logging.getLogger(__name__)
    sys.exit(main())
