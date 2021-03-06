#!/bin/bash
set -e


#--------------------------------------------------
# Static variables
#--------------------------------------------------

# Version used for update checks, updated on each (significant) commit, double quotes required because bash...
VERSION="'0.0.17'"

# Main library directory
LIB_DIR=/var/lib/kvm-install-vm

# Simple config checker
NUM_CONFIGS=$(ls -1 $LIB_DIR | grep -v cloud.cfg | wc -l)

# Pip packages
PIP_PKGS="PyYAML python-dotenv ansible GitPython ansible-subprocess"



#--------------------------------------------------
# Installer
#--------------------------------------------------

# Console output colors
bold() { echo -e "\e[1m$@\e[0m" ; }
red() { echo -e "\e[31m$@\e[0m" ; }
green() { echo -e "\e[32m$@\e[0m" ; }
yellow() { echo -e "\e[33m$@\e[0m" ; }

die() { red "ERROR: $@" >&2 ; exit 2 ; }
silent() { "$@" > /dev/null 2>&1 ; }
output() { echo -e "- $@" ; }
outputn() { echo -en "- $@ ... " ; }
ok() { green "${@:-OK}" ; }

subcommand="${1:-none}"
[[ "${subcommand}" != "none" ]] && shift

function check_pip ()
{
    ok "Checking pip installation"
    OS_VERSION=`awk -F= '/^NAME/{print $2}' /etc/os-release`
    isPip=`which pip | grep -cv no`
    if [ $isPip -lt 1 ]; then
        if [[ "${varFromIF=$(echo $OS_VERSION | grep -ic 'centos')}" -eq 1 ]]; then
            yum install -y python-pip
        fi
        if [[ "${varFromIF=$(echo $OS_VERSION | grep -ic 'ubuntu')}" -eq 1 ]]; then
            apt install -y python-pip
        fi
    fi

    # Do one last check before continuing
    isPip=`which pip | grep -cv no`
    if [ $isPip -lt 1 ]; then
        die "Was unable to install pip, please install manually then run this again."
    fi
}

function install_deps ()
{
    ok "Installing pip dependencies"
    for pkg in $PIP_PKGS; do
        if [ $(pip list | grep -i $pkg | head -1 | wc -l) -ne 1 ]; then
            pip install $pkg
        else
            yellow "Skipping $pkg as it's already installed..."
        fi
    done
}

function cleanup ()
{
    ok "Cleaning up"
    rm -rf $LIB_DIR/*
    rm -f /usr/sbin/kvm-install-vm
    rm -f /usr/local/bin/bootstrap.py
}

function setup ()
{
    git clone https://github.com/SurrealTiggi/kvm-install-vm.git /tmp/kvm

    ok "Setting up libraries"
    mv /tmp/kvm/lib/* $LIB_DIR/
    ok "Setting up main runner"
    mv /tmp/kvm/kvm-install-vm /usr/sbin/kvm-install-vm
    chmod +x /usr/sbin/kvm-install-vm
    ok "Setting up bootstrap.py"
    mv /tmp/kvm/bootstrap.py /usr/local/bin/bootstrap.py
    chmod +x /usr/local/bin/bootstrap.py
    ok "Setting up cloud-init template"
    mv /tmp/kvm/cloud.cfg $LIB_DIR/cloud.cfg
    ok "Setup-ception"
    mv -f /tmp/kvm/setup.sh ./setup.sh
    chmod +x ./setup.sh
    rm -rf /tmp/kvm
}


case "${subcommand}" in
    --source-only)
        ok "Import only"
        ;;
    --install)
        if [ ! -d "$LIB_DIR" ] || [ $NUM_CONFIGS -lt 6 ]; then
            mkdir -p $LIB_DIR
            cleanup
            setup
        else
            ok "Libraries found so continuing..."
        fi

        check_pip
        install_deps
        ok "DONE!"
        # TODO: 
        # 1) Move .kivrc check from utils lib to here???
        ;;
    --update)
        NEW_VERSION=$(curl https://raw.githubusercontent.com/SurrealTiggi/kvm-install-vm/master/setup.sh | grep 'VERSION' | head -1 | cut -f2 -d'=' | sed -e 's/\"//g')
        ok "Checking for updates..."
        if [[ $VERSION != $NEW_VERSION ]]; then
            yellow "Update found!"
            cleanup
            setup
            check_pip
            . setup.sh --source-only
            install_deps
        else
            ok "No updates found"
        fi
        ;;
    --remove)
        cleanup
        ;;
    *)
        die "'${subcommand}' is not a valid subcommand.  Usage: ./setup.sh --install|--update|--remove."
        ;;
esac
