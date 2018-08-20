#!/usr/bin/env python2

'''
This is a basic script to do base setups on cloud instances, runs alongside cloud-init after an instance is provisioned.
Can also be run separately to check ansible inventory.
'''

# Imports
import sys
import logging
import os
from os.path import expanduser
import requests
import re
import argparse
import traceback
from collections import OrderedDict

import git
from git import Repo
import yaml
from yaml import load, dump
from dotenv import load_dotenv
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.executor.playbook_executor import PlaybookExecutor
#from ansible_vault import Vault

# Static variables
FORMAT = '%(asctime)s -- %(levelname)s -- [ %(filename)s:%(lineno)s - %(funcName)s() ] : %(message)s'
ANSIBLE_INV = None
ANSIBLE_GIT = None
VAULT_PWD = None
if os.name == 'nt':
    LOGFILE = str(os.getcwd() + '\\bootstrap.log')
    HOME = str(expanduser("~") + '\\')
    ENV_FILE = str(HOME + '.kivrc')
    ANSIBLE_HOSTS = None

else:
    LOGFILE = str(os.getcwd() + '/bootstrap.log')
    HOME = str(expanduser("~") + '/')
    ENV_FILE = str(HOME + '.kivrc')
    ANSIBLE_HOSTS = '/etc/ansible/hosts'

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

def ansibleHelper(vault=None):
    '''
    Creates the ansible inventory object
    
    TODO: Split out into its own class???
    '''
    data_loader = DataLoader()

    if vault is not None:
        data_loader.set_vault_password(vault)

    inv = InventoryManager(loader = data_loader,
                                    sources=[ANSIBLE_HOSTS])
    return inv

def ansibleDiff(priv, local):
    '''
    Check for differences between inventory.yml object and ansible inventory object
    
    TODO: Cleanup missing since it includes entries we don't necessarily want
    TODO: Return True/False depending on actual differences
    '''
    missing = set(priv['hosts'].keys()) - set(local)
    return False

def updateLocal():
    '''
    Update local inventory to match private inventory
    TODO: yeah...
    '''
    pass


def fetchInventory(url):
    '''
    Fetch personalized inventory.yml from given location
    
    TODO: If gist.github.com, convert to correct raw location
    '''

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

def validateInventory(instance=None):    
    '''
    Main inventory validator, if any issues are experienced, simply throw an exception and exit.
    Either follow the expected template, or fail.

    TODO:
    5) Setup ~/.ansible.cfg using variables from .kivrc

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

    log.debug("Validating inventory...")

    try:
        # Load the inventory file into an easily queryable object that we can loop through
        with open(HOME + 'inventory.yml', 'r') as myfile:
            myinventory = myfile.read()
        private_inv = yaml.load(myinventory)


        # TODO: Don't loop...
        # Loop through each inventory key and act accordingly
        # Get the git flag since it's used a few times
        git_enabled = private_inv['git']['enabled']
        for key, value_dict in private_inv.items():
            # If git is ENABLED, download git project and we're done
            if key == 'git' and git_enabled:
                ANSIBLE_GIT = str(re.findall('/(\w+)?.git$', value_dict['location'])[0] + '/')
                if os.path.exists(HOME + ANSIBLE_GIT):
                    log.debug('Directory ' + ANSIBLE_GIT + ' exists so updating...')
                    g = git.cmd.Git(HOME + ANSIBLE_GIT)
                    g.pull()
                else:
                    log.debug('Directory ' + ANSIBLE_GIT + ' non-existant so pulling...')
                    Repo.clone_from(value_dict['location'], HOME + ANSIBLE_GIT)
            # If vault is ENABLED, set it up
            if key == 'config' and value_dict['vault']['enabled']:
                VAULT_PWD = value_dict['vault']['password']
            # If git is DISABLED, fetch defaults and the relevant playbook
            if key == 'config' and not git_enabled:
                log.debug('Attempting to download defaults.yml')
                defaults = private_inv['config']['defaults']['location']
                r = requests.get(str(defaults))
                open(HOME + 'defaults.yml', 'wb').write(r.content)
            if key == 'hosts' and not git_enabled:
                for host, value_dict in private_inv['hosts'].items():
                    if host == instance:
                        log.debug('Attempting to download ' + instance + '.yml')
                        r = requests.get(str(value_dict['location']))
                        open(HOME + instance, 'wb').write(r.content)

        # Not super happy with this being here, need to fix
        if git_enabled:
            open(HOME + ANSIBLE_GIT + 'vault-pass.txt').write(VAULT_PWD)
        else:
            open(HOME + 'vault-pass.txt').write(VAULT_PWD)

        # Create a simple string list of all ansible hostnames
        ANSIBLE_INV = ansibleHelper(vault=VAULT_PWD)
        local_inv = [str(i.name) for i in ANSIBLE_INV.groups.values()]

        if ansibleDiff(private_inv, local_inv):
            updateLocal()

    except Exception as e:
        log.error('Failed to process inventory.yml file: ' + str(e))
        traceback.print_tb(e.__traceback__)
        print(Colors.FAIL + 'Unable to continue as your inventory file is un-readable. Please check it and re-run this script.')
        sys.exit()

def runAnsible(instance):
    log.debug("Playbooking >> " + instance)

    if ANSIBLE_GIT is not None:
        playbook_path = HOME + ANSIBLE_GIT + instance + '.yml'
    else:
        playbook_path = HOME + instance + '.yml'
    
    pbex = PlaybookExecutor(playbooks=playbook_path, inventory=ANSIBLE_INV)

    results = pbex.run()
    
def cleanup():
    log.debug('Cleaning up...')
    try:
        os.remove(HOME + 'inventory.yml')
    except OSError as e:
        log.error('Failed to remove inventory.yml: ' + e)
        pass


def promptUser():

    answer = input(Colors.OKBLUE + 'Please specify the URL location of inventory.yml: \n\t')

    while not fetchInventory(answer):
        print(Colors.WARNING + 'Invalid URL given. Please retry...')
        promptUser()
    # TODO: Write into .kivrc
    
def main(*args, **kwargs):
    '''
    Bootstrapping utility/ansible wrapper for cloud-init VMs, works as follows:
    * Checks if inventory.yml is defined in local .kivrc
    * If not, requests location to fetch it (a URL by default)
    * Once the file is present, ALWAYS parse it, ALWAYS validate local inventory, then run ansible-playbooks (if an instance is provided)
    * When finished, delete inventory.yml. That way, the external source remains canonical.
    '''

    log.debug("Starting bootstrap...")

    load_dotenv(dotenv_path=ENV_FILE)
    INV_URL = os.getenv("INV_URL")

    if INV_URL:
        if not fetchInventory(INV_URL):
            log.error("Invalid URL found in .kivrc, switching to prompt...")
            promptUser()
    else:
        log.debug("No $INV_URL defined, prompting user for web location")
        promptUser()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--instance", type=str,
                        help="singular instance to configure",
                        default=None)
    args, _ = parser.parse_known_args()

    validateInventory(instance=args.instance)

    if args.instance:
        runAnsible(args.instance)
    else:
        log.debug("No instance given so just cleaning up")
        cleanup()

if __name__ == '__main__':
    logging.basicConfig(format=FORMAT, filename=LOGFILE, level=os.environ.get("LOGLEVEL", "DEBUG"))
    log = logging.getLogger(__name__)
    sys.exit(main())
