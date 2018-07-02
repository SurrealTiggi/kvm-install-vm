## kvm-install-vm

A bash wrapper around virt-install to build virtual machines on a local KVM
hypervisor.  You can run it as a normal user which will use `qemu:///session` to
connect locally to your KVM domains.

Adapted to work specifically for my own personal use-cases

### Prerequisites

You need to have the KVM hypervisor installed, along with a few other packages:

- genisoimage or mkisofs
- virt-install
- libguestfs-tools
- qemu-img
- libvirt-client
- libnss-libvirt

Then, add `libvirt` and `libvirt_guest` to list of **hosts** databases in
`/etc/nsswitch.conf`.  See [here](https://libvirt.org/nss.html) for more
information.

### Usage

```
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

```
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
    -D          DNS Domain          (default: crypticmonsters.com)
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

#### Deleting a Guest Domain

```
$ kvm-install-vm help remove
NAME
    kvm-install-vm remove [COMMANDS] VMNAME

DESCRIPTION
    Destroys (stops) and undefines a guest domain.  This also remove the
    associated storage pool.

COMMANDS
    help - show this help

EXAMPLE
    kvm-install-vm remove foo
        Remove (destroy and undefine) a guest domain.  WARNING: This will
        delete the guest domain and any changes made inside it!
```

#### Attaching a new disk

```
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

### Setting Custom Defaults

Copy the `.kivrc` file to your $HOME directory to set custom defaults.  This is
convenient if you find yourself repeatedly setting the same options on the
command line, like the distribution or the number of vCPUs.

Options are evaluated in the following order:

- Default options set in the script
- Custom options set in `.kivrc`
- Option flags set on the command line

### Testing

Tests are written using [Bats](https://github.com/sstephenson/bats).  To
execute the tests, run `./test.sh` in the root directory of the project.