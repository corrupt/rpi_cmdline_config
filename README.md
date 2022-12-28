# Ansible rpi_cmdline_config
Ansible module to modify or set Raspberry Pi /boot/cmdline.txt arguments.

## Example Playbook

```yaml
- name: "Configure RPi cmdline.txt"
  rpi_cmdline_config:
    cmdline: /boot/cmdline.txt
    key: modules-load
    values: dwc2,g_ether
    unique: true
    after: rootwait
  become: true
  notify: reboot
```
```cmdline``` has a default of ```'/boot/cmdline.txt'```
It is possible to set ```key=value``` pairs or single atoms. Both are mutually exclusive:

```yaml
- name: "Add rootwait to cmdline.txt"
  rpi_cmdline_config:
    atom: rootwait
    after: fsck.repair
    unique: true
```

The ```unique``` parameter makes sure that a key or atom is only ever set once. It can be used to add values to an existing key as well.

## Installation

```ansible-galaxy``` doesn't support the installation of modules from github. Custom modules can be installed by copying the main file (in this case ```rpi_cmdline_config.py```) to the ```library``` folder inside the Ansible directory structure.