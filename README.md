# kvm-install-vm

[![Generic badge](https://img.shields.io/badge/Version-0.0.15-GREEN.svg)](https://shields.io/)

[![N|Solid](https://i.imgur.com/f6CyxB4.png)](https://libvirt.org/)

A bash wrapper around virt-install to build virtual machines on a local KVM
hypervisor.  You can run it as a normal user which will use `qemu:///session` to
connect locally to your KVM domains.

> **Adapted to work specifically for my own personal use-cases.**

## Workflow

```sh
=> kvm-install-vm create <vm_name>
=> ~/.kivrc and ~/bootstrap.py get setup
=> <vm_name> base provisioned with cloud-init
=> script.sh runs inside VM (if any)
=> bootstrap.py kicks off ansible playbook for <vm_name> (runs locally, *not* from inside the VM)
```

## Prerequisites

You need to have the KVM hypervisor installed, along with a few other packages:

- genisoimage or mkisofs
- virt-install
- libguestfs-tools
- qemu-img
- libvirt-client
- libnss-libvirt
- git (only if you use bootstrap.py)
- pip (NB. --install will sort these dependencies out...hopefully)
  - GitPython
  - PyYaml
  - Python-DotEnv
  - Ansible
  - Ansible-Vault

Then, add `libvirt` and `libvirt_guest` to list of **hosts** databases in
`/etc/nsswitch.conf`.  See [here](https://libvirt.org/nss.html) for more
information.

## Installation

Trying to go for a simpler approach, basically you should just need to download [setup.sh](https://raw.githubusercontent.com/SurrealTiggi/kvm-install-vm/master/setup.sh), `chmod +x install.sh`, and then `./setup.sh --install`.

On every run the script checks that:

- `~/.kivrc` exists, if not, an interactive dialog kicks off to fetch it and fill it out with any custom flags the user wants.

> **NOTE!**
> When a VM is provisioned, and if you're making use of it, you may be asked for the location of `inventory.yml`.
> An example of this file is provided [inventory_sample.yml](https://raw.githubusercontent.com/SurrealTiggi/kvm-install-vm/master/inventory_sample.yml).
> This file is based on using ansible to manage a small number of VMs, so skip it if you're not using it.
> The point of this file is in case there are customizations in the ansible playbook that need to be kept private, as well as providing a single file to keep track of all VM's.
> If you don't want to use it, just keep SCRIPT and ORC_SCRIPT flags blank in your `.kivrc` file.
> The formatting is pretty strict, not perfect, but strict nonetheless.

- `~/cloud.cfg` cloud-init config exists, else it prompts to reinstall.

### Usage

```sh
$ kvm-install-vm help
NAME
    kvm-install-vm - Install virtual guests using cloud-init on a local KVM
    hypervisor.

SYNOPSIS
    kvm-install-vm COMMAND [OPTIONS]

DESCRIPTION
    A bash wrapper around virt-install to build virtual machines on a local KVM
    hypervisor. You can run it as a normal user which will use qemu:///session
    to connect locally to your KVM domains.

COMMANDS
    help    - show this help or help for a subcommand
    create  - create a new guest domain
    list    - list all domains, running and stopped
    remove  - delete a guest domain
```

#### Creating Guest VMs

```sh
$ kvm-install-vm help create
NAME
    kvm-install-vm create [OPTIONS] VMNAME

DESCRIPTION
    Create a new guest domain.

OPTIONS
    -a          Autostart           (default: false)
    -b          Bridge              (default: br0)
    -c          Number of vCPUs     (default: 1)
    -d          Disk Size (GB)      (default: 10)
    -D          DNS Domain          (default: example.local)
    -f          CPU Model / Feature (default: host)
    -g          Graphics type       (default: vnc)
    -h          Display help
    -i          Custom QCOW2 Image
    -k          SSH Public Key      (default: $HOME/.ssh/id_rsa.pub)
    -l          Location of Images  (default: $HOME/virt/images)
    -m          Memory Size (MB)    (default: 1024)
    -M mac      Mac address         (default: auto-assigned)
    -p          Console port        (default: auto)
    -s          Custom shell script
    -t          Linux Distribution  (default: centos7)
    -T          Timezone            (default: Europe/Dublin)
    -u          Custom user         (default: $USER)
    -v          Be verbose

DISTRIBUTIONS
    NAME            DESCRIPTION                         LOGIN
    centos7         CentOS 7                            centos
    centos7-atomic  CentOS 7 Atomic Host                centos
    ubuntu1604      Ubuntu 16.04 LTS (Xenial Xerus)     ubuntu

EXAMPLES
    kvm-install-vm create foo
        Create VM with the default parameters: CentOS 7, 1 vCPU, 1GB RAM, 10GB
        disk capacity.

    kvm-install-vm create -c 2 -m 2048 -d 20 foo
        Create VM with custom parameters: 2 vCPUs, 2GB RAM, and 20GB disk
        capacity.

    kvm-install-vm create -t debian9 foo
        Create a Debian 9 VM with the default parameters.

    kvm-install-vm create -T UTC foo
        Create a default VM with UTC timezone.

    kvm-install-vm create -s ~/script.sh -g vnc -u bar foo
        Create a VM with a custom script included in user-data, a graphical
        console accessible over VNC, and a user named 'bar'.
```

#### Attaching a new disk

```sh
$ kvm-install-vm help attach-disk
NAME
    kvm-install-vm attach-disk [OPTIONS] [COMMANDS] VMNAME

DESCRIPTION
    Attaches a new disk to a guest domain.

COMMANDS
    help - show this help

OPTIONS
    -d SIZE     Disk size (GB)
    -f FORMAT   Disk image format       (default: qcow2)
    -s IMAGE    Source of disk device
    -t TARGET   Disk device target

EXAMPLE
    kvm-install-vm attach-disk -d 10 -s example-5g.qcow2 -t vdb foo
        Attach a 10GB disk device named example-5g.qcow2 to the foo guest
        domain.
```

## TODO:

- [x] Implement inventory -> ansible
- [ ] Finalize bootstrap.py
- [x] Implement --install|--update|--remove options for easy management of new features/any updates
- [ ] Packaging (.rpm, .deb) and build status via Jenkins ???
- [ ] Update README.md when all the above is done