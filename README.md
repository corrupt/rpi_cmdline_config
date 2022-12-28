# Ansible rpi_cmdline_config
Ansible module to modify or set Raspberry Pi /boot/cmdline.txt arguments.

## Options

```yaml
cmdline: Location of cmdline.txt (default: '/boot/cmdline.txt')
key: Key to add (requires 'value')
values: List of values to add to 'key'
atom: Single keyword to add (not a key=value pair. Mutually exclusive with 'key' and 'values')
unique: Ensure that key or atom are only present once
before: Key or atom before which the new entry should be set (mutually exclusive with 'after')
after:  Key or atom after which the new entry should be added (mutually exclusive with 'before')
```

## Example Playbook

```yaml
- name: "Configure RPi cmdline.txt"
  rpi_cmdline_config:
    cmdline: /boot/cmdline.txt
    key: modules-load
    values: dwc2,g_ether
    unique: true
    after: fsck.repair
  become: true
  notify: reboot
```
Will turn a default cmdline.txt from
```
console=serial0,115200 console=tty1 root=PARTUUID=01234678-90 rootfstype=ext4 fsck.repair=yes rootwait
```
to
```
console=serial0,115200 console=tty1 root=PARTUUID=01234678-90 rootfstype=ext4 fsck.repair=yes modules-load=dwc2,g_ether rootwait
```


```cmdline``` has a default of ```'/boot/cmdline.txt'```
It is possible to set ```key=value``` pairs or single atoms. Both are mutually exclusive:

```yaml
- name: "Add rootwait to cmdline.txt"
  rpi_cmdline_config:
    atom: quiet
    after: rootwait
    unique: true
```
Will turn a default cmdline.txt from
```
console=serial0,115200 console=tty1 root=PARTUUID=01234678-90 rootfstype=ext4 fsck.repair=yes rootwait
```
to
```
console=serial0,115200 console=tty1 root=PARTUUID=01234678-90 rootfstype=ext4 fsck.repair=yes rootwait quiet
```

The ```unique``` parameter makes sure that a key or atom is only ever set once. It can be used to add values to an existing key as well.

## Installation

```ansible-galaxy``` doesn't support the installation of modules from github. Custom modules can be installed by copying the main file (in this case ```rpi_cmdline_config.py```) to the ```library``` folder inside your Ansible directory.