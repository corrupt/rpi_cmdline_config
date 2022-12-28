#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: rpi_cmdline_txt

short_description: Module for easy modification of a Raspberry Pi /boot/cmdline.txt

version_added: "0.1.0"

description: Set or change parameters in /boot/cmdline.txt on a Raspberry Pi.

options: 
    cmdline:
        description: Location of the cmdline.txt file
        required: false
        type: str
        default: '/boot/cmdline.txt'
    key:
        description: New Key to add to the cmdline or key to add values to. Mutually exclusive with I(atom)
        required: false 
        type: str
    values:
        description:
            - Values to add to the key.
            - Depending on the value of I(unique) these values will be added to an existing key, if any, or to a new one
            - Required in combination with I(key). Cannot be set with 'atom'.
        required: false
        type: list
    atom:
        description:
            - Single atom (a key without value) to add to the cmdline. Will not add an '=' after.
            - Mutually exclusive with I(key) and I(value)
        required: false
        type: str
    unique:
        description:
            - Whether or not the new key or atom must be unique
            - If set to false, a new atom or key=value pair will be added.
            - If set to true (the default), values will be added to an existing key and a second atom will not be added
        required: false
        type: bool
        default: true
    after:
        description:
            - For key=value pairs or atoms that need others to be there first (like 'rootwait'), pass the one after which to add them here
        required: false
        type: str
        default: false

author:
    - corrupt (@corrupt)    
'''

EXAMPLES = r'''
# Add USB OTG support
- name: Add modules-load with dwc2 and g_ether
  rpi_cmdline_txt:
    key: modules-load
    values: [dwc2, g_ether]
    after: rootwait
'''

RETURN = r''' # ''' 

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator


def tokenize(input: str) -> list:
    tokens = input.split()
    parsed = []
    for token in tokens:
        key, *value = token.split("=", 1)
        if value == []:
            values = None
        else:
            values = value[0].split(",")
        parsed.append({'key': key, 'value': values})
    return parsed


def add_param(params: list, key: str, values: list, after: str = None, unique: bool = True) -> dict:
    new = {'key': key, 'value': values}

    if unique and has_param(params, key):
        for i, pair in enumerate(params):
            if pair['key'] == key and values is not None:
                for value in values:
                    if value not in pair['value']:
                        pair['value'].append(value)
    else:
        if after is None:
            params.append(new)
        else:
            params.reverse()
            for i, pair in enumerate(params):
                if pair['key'] == after:
                    params.insert(i, new)
                    params.reverse()
                    return params
            params.reverse()
            params.append(new)
    return params


def has_param(params: list, key: str) -> bool:
    for pair in params:
        if pair['key'] == key:
            return True
    return False


def to_string(params: list) -> str:
    ret = ""
    for pair in params:
        key = pair['key']
        value = pair['value']
        if value is None:
            ret += f"{key} "
        elif isinstance(value, list):
            ret += f"{key}={','.join(value)} "
        else:
            ret += f"{key}={value} "
    return ret.strip()


def run_module():
    module_args = dict(
        cmdline = dict(type='str', default="/boot/cmdline.txt"),
        key = dict(type='str', default=None),
        values = dict(type='list', elements='str', default=None),
        atom = dict(type='str', default=None),
        unique = dict(type='bool', default=True),
        after = dict(type='str', default=None),
    )
    mutually_exclusive = [
        ('key', 'atom'),
        ('values', 'atom')
    ]
    required_one_of = [
        ('atom', 'key')
    ]
    required_together = [
        ('key', 'values')
    ]

    result = dict(
        changed=False,
        original_message='',
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=mutually_exclusive,
        required_one_of=required_one_of,
        required_together=required_together,
        supports_check_mode=False,
    )

    validator = ArgumentSpecValidator(
        argument_spec=module_args,
        mutually_exclusive=mutually_exclusive,
        required_one_of=required_one_of,
        required_together=required_together,
    )

    validation_result = validator.validate(module.params)

    filename = module.params['cmdline']
    key = module.params['key']
    values = module.params['values']
    atom = module.params['atom']
    after = module.params['after']
    unique = module.params['unique']

    try:
        with open(filename, 'r') as f:
            cmdline = f.read()

        params = tokenize(cmdline)

        if key is not None and values is not None:
            params = add_param(params, key, values, after, unique)
        elif atom is not None:
            params = add_param(params, atom, None, after, unique)

        new_cmdline = to_string(params)

        with open(filename, 'w') as f:
            f.write(f"{new_cmdline}\n")

        result['changed'] = cmdline != new_cmdline
        result['message'] = f"New cmdline: '{new_cmdline}'"
        result['original_message'] = f"Old cmdline: '{cmdline}'"
    except IOError as e:
        module.fail_json(msg=f"Unable to modify {filename}: {e}", **result)
    
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()