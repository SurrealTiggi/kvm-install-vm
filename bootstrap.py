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

def runAnsible():
    log.debug('Running ')

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

def bootstrap():
    validateInventory()
    runAnsible()
    
def main(argv=None):
    '''
    Bootstrapping utility for cloud-init VMs, works as follows:
    * Checks if inventory.yml exists in current user's $HOME
    * If not, requests location to fetch it (a URL by default)
    * Once the file is present, parse it and run ansible against the provisioned VM
    '''
    log.debug("Starting bootstrap...")
    if not os.path.isfile(HOME + 'inventory.yml'):
        promptUser()
        bootstrap()
    else:
        bootstrap()

if __name__ == '__main__':
    logging.basicConfig(format=FORMAT, filename=LOGFILE, level=os.environ.get("LOGLEVEL", "DEBUG"))
    log = logging.getLogger(__name__)
    sys.exit(main())