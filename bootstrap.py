#!/usr/bin/env python2

'''
This is a basic script to do base setups on cloud instances, runs alongside cloud-init after an instance is provisioned
TODO:
2) Set up local inventory for ansible including ~/.ansible.cfg
3) Run ansible playbook against single vm if being called from kvm-install-vm create
'''

# Imports
import sys
import logging
import os
from os.path import expanduser
import requests
import re
import argparse
from collections import OrderedDict

import yaml
from yaml import load, dump
from dotenv import load_dotenv
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

# Static variables
FORMAT = '%(asctime)s || %(levelname) || [%(filename)s:%(lineno)s - %(funcName)20s() ] : %(message)s'
if os.name == 'nt':
    LOGFILE = str(os.getcwd() + '\\bootstrap.log')
    HOME = str(expanduser("~") + '\\')
    ENV_FILE = str(HOME + '.kivrc')
    ANSIBLE_INV = None

else:
    LOGFILE = str(os.getcwd() + '/bootstrap.log')
    HOME = str(expanduser("~") + '/')
    ENV_FILE = str(HOME + '.kivrc')
    ANSIBLE_INV = '/etc/ansible/hosts'

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

def ansibleHelper():
    # TODO: Split out into its own class???
    data_loader = DataLoader()
    ansible_inv = InventoryManager(loader = data_loader,
                                    sources=[ANSIBLE_INV])
    return ansible_inv


def fetchInventory(url):
    # TODO: If gist.github.com, convert to correct raw location
    try:
        r = requests.get(str(url))

        if r.status_code != 200:
            print(Colors.WARNING + 'Non-existant URL given. Please retry...')
            return False
        else:
            print(Colors.OKGREEN + "Valid URL given, saving inventory")
            open(HOME + 'inventory.yml', 'wb').write(r.content)
            return True
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
        ansible_inv = ansibleHelper()

        # Create a simple string list of all ansible hostnames
        gospel_inv = [str(i.name) for i in ansible_inv.groups.values()]

        missing = set(inv['hosts'].keys()) - set(gospel_inv)



        '''
        TODO:
        1) Wipe /etc/ansible/hosts and rebuild each time from inventory.yml
        2) If git[enabled] = true -> Book out the entire project and ansible-playbook ansible_scripts/<host>
        3) If git[enabled] = false -> Grab defaults.yml
        4) Get singular playbook -> Download the relevant playbook and ansible-playbook ansible_scripts/<host>

        case = OrderedDict([
            ('1', function1),
            ('2', function2),
        ])

        case[1]() or case[2]()

        if choice in case:
            case[choice]()
            
        for key, value in case.items():
            print('%s) %s') % (key, value.__doc__)
        '''

        for key, value in inv.items():
            if key == 'git':
                # TODO: Book out git repo into ansible_scripts folder
                # TODO: If it exists already, then just run an update
                # TODO: Setup ~/.ansible.cfg using variables from .kivrc
                pass
            elif key == 'config':
                pass


    except Exception as e:
        log.error('Failed to process inventory.yml file: ' + str(e))
        print(Colors.FAIL + 'Unable to continue as your inventory file is un-readable. Please check it and re-run this script.')
        sys.exit()

def runAnsible(instance):
    # TODO: If inv.repo = True then run from inside ansible_scripts directory
    log.debug('Running with ' + instance)

def cleanup():
    log.debug('Cleaning up...')

def promptUser():

    answer = input(Colors.OKBLUE + 'Please specify the URL location of inventory.yml: \n\t')

    while not fetchInventory(answer):
        print(Colors.WARNING + 'Invalid URL given. Please retry...')
        promptUser()
    # TODO: Write into .kivrc
    
def main(instance):
    '''
    Bootstrapping utility for cloud-init VMs, works as follows:
    * Checks if inventory.yml is defined in local .kivrc
    * If not, requests location to fetch it (a URL by default)
    * Once the file is present, parse it, validate local inventory, then run ansible-playbooks
    * When finished, delete inventory.yml. That way, the external source remains canonical.
    '''
    log.debug("Starting bootstrap...")
    load_dotenv(dotenv_path=ENV_FILE)
    INV_URL = os.getenv("INV_URL")

    if INV_URL:
        if not fetchInventory(INV_URL):
            log.error("Invalid URL found in .kivrc, switching to prompt...")
            promptUser()
        validateInventory()
        runAnsible(instance)
        cleanup()
    else:
        log.debug("No $INV_URL defined, prompting user for web location")
        promptUser()
        validateInventory()
        runAnsible(instance)
        cleanup()

if __name__ == '__main__':
    logging.basicConfig(format=FORMAT, filename=LOGFILE, level=os.environ.get("LOGLEVEL", "DEBUG"))
    log = logging.getLogger(__name__)
    sys.exit(main(None))


