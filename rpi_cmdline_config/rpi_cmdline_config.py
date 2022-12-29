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
    before:
        description:
            - For key=value pairs or atoms that need to be present before others (like 'rootwait'), pass the one before which to add them here
            - Mutually exclusive with I(after)
        required: false
        type: str
        default: false
    after:
        description:
            - For key=value pairs or atoms that need others to be there first (like 'rootwait'), pass the one after which to add them here
            - Mutually exclusive with I(before)
        required: false
        type: str
        default: false

author:
    - corrupt (@corrupt)    
''' # noqa: 501

EXAMPLES = r'''
# Add USB OTG support
- name: Add modules-load with dwc2 and g_ether
  rpi_cmdline_txt:
    key: modules-load
    values: [dwc2, g_ether]
    after: rootwait
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule  # noqa: 402
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator  # noqa: 402


class KernelParams:

    params: list = []

    def __init__(self, cmdline: str):
        self.params = self._tokenize(cmdline)

    def _tokenize(self, input: str) -> list:
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

    # noqa: C901
    def add_param(
        self,
        key: str,
        values: list,
        before: str = None,
        after: str = None,
        unique: bool = True
    ) -> 'KernelParams':
        new = {'key': key, 'value': values}

        new_params = self.params.copy()

        if unique and self.has_param(key):
            for i, pair in enumerate(new_params):
                if pair['key'] == key and values is not None:
                    for value in values:
                        if value not in pair['value']:
                            pair['value'].append(value)
        elif after is not None:
            new_params.reverse()
            for i, pair in enumerate(new_params):
                if pair['key'] == after:
                    new_params.insert(i, new)
                    new_params.reverse()
                    self.params = new_params
                    return self
            new_params.reverse()
            new_params.append(new)
        elif before is not None:
            for i, pair in enumerate(new_params):
                if pair['key'] == before:
                    new_params.insert(i, new)
                    self.params = new_params
                    return self
            new_params.append(new)
        else:
            new_params.append(new)
        self.params = new_params
        return self

    def has_param(self, key: str) -> bool:
        for pair in self.params:
            if pair['key'] == key:
                return True
        return False

    def to_string(self) -> str:
        ret = ""
        for pair in self.params:
            key = pair['key']
            value = pair['value']
            if value is None:
                ret += f"{key} "
            elif isinstance(value, list):
                ret += f"{key}={','.join(value)} "
            else:
                ret += f"{key}={value} "
        return ret.strip()


# -------------------------------------------------------------------------- #


def run_module():
    module_args = dict(
        cmdline=dict(type='str', default="/boot/cmdline.txt"),
        key=dict(type='str'),
        values=dict(type='list', elements='str'),
        atom=dict(type='str'),
        unique=dict(type='bool'),
        after=dict(type='str'),
        before=dict(type='str'),
    )
    mutually_exclusive = [
        ('key', 'atom'),
        ('before', 'after'),
    ]
    required_one_of = [
        ('atom', 'key'),
    ]
    required_together = [
        ('key', 'values'),
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

    validation_result = validator.validate(
        {k: v for k, v in module.params if v is not None}
    )

    if validation_result.error_messages:
        result['message'] = ",".join(validation_result.error_messages)
        module.fail_json(
            msg="Failed parameter validation",
            **result
        )

    filename = module.params['cmdline']
    key = module.params['key']
    values = module.params['values']
    atom = module.params['atom']
    after = module.params['after']
    before = module.params['before']
    unique = module.params['unique']

    try:
        with open(filename, 'r') as f:
            cmdline = f.read().strip()

        params = KernelParams(cmdline)

        if key is not None and values is not None:
            params.add_param(key, values, before, after, unique)
        elif atom is not None:
            params.add_param(atom, None, before, after, unique)

        new_cmdline = params.to_string()

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
