#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
module: cloud_provider_account
short_description: Manages an RHSM Cloud Access provider account
description: >
  This module will ensure a cloud provider account exists in RHSM and optionally
  verifies it for use with auto registration.
options:
  state:
    description:
      - Add or remove a cloud provider account
    choices: [ present, absent ]
    default: present
    type: str
  refresh_token:
    description:
      - Offline refresh token for authentication with Red Hat APIs
      - Tokens can be generated at https://access.redhat.com/management/api
    required: true
    type: str
  refresh_token_client:
    description:
      - Client ID used to generate the refresh token
      - Typically 'rhsm-api' for tokens generated at access.redhat.com and 'cloud-services' for cloud.redhat.com
    default: rhsm-api
    type: str
  provider:
    description:
      - Short Name of the cloud provider
    choices: [ AWS, MSAZ, GCP ]
    required: true
    type: str
  id:
    description:
      - Account ID of the cloud provider account
    required: true
    type: str
  nickname:
    description:
      - Nickname or short description of the cloud provider account
    type: str
  verification_identity:
    description:
      - Cloud VM instance identity document
      - Only needed to verify a cloud provider account for use with RHSM auto registration
    type: str
  verification_signature:
    description:
      - Cloud VM instance identity signature
      - Only needed to verify a cloud provider account for use with RHSM auto registration
    type: str
author:
  - Patrick Easters (@patrickeasters)
requirements:
  - requests-oauthlib
'''

EXAMPLES = '''
- name: Create a cloud provider account
  redhatinsights.subscriptions.cloud_provider_account:
    provider: AWS
    id: 123456789012
    nickname: my pretty neat aws account
    refresh_token: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1kUXc0dzlXZ1hjUQo=

- name: Delete a provider account
  redhatinsights.subscriptions.cloud_provider_account:
    provider: MSAZ
    id: c11d7e74-adb4-4ce3-9a07-93c7a6f88cdf
    state: absent
    refresh_token: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1kUXc0dzlXZ1hjUQo=

- name: Verify an account for use with auto registration
  redhatinsights.subscriptions.cloud_provider_account:
    provider: AWS
    id: 123456789012
    verification_identity: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1XYWFBTmxsOGgxOAo=
    verification_signature: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1pblhDX2xhYi0zNAo=
    refresh_token: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1kUXc0dzlXZ1hjUQo=
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.redhatinsights.subscriptions.plugins.module_utils.rhapi import RedHatAPIClient


def return_changed(module):
    result = dict(changed=True)
    module.exit_json(**result)


def run_module():
    module_args = dict(
        state=dict(choices=['present', 'absent'], default='present'),
        refresh_token=dict(type='str', required=True),
        refresh_token_client=dict(type='str', default='rhsm-api'),
        provider=dict(type='str', required=True),
        id=dict(type='str', required=True),
        nickname=dict(type='str', required=False, default=''),
        verification_identity=dict(type='str', required=False, default=''),
        verification_signature=dict(type='str', required=False, default=''),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    client = RedHatAPIClient(module)

    # Get existing cloud providers
    enabled = client.get('/cloud_access_providers/enabled')
    if enabled.status_code != 200:
        module.fail_json(msg="Failed to retrieve provider accounts")
    providers = enabled.json()

    # Find existing account in list of enabled providers
    account = {}
    if providers['body']:
        for p in providers['body']:
            if p['shortName'] == module.params['provider']:
                for a in p['accounts']:
                    if a['id'] == module.params['id']:
                        account = a
                        break
                break

    # Delete account if needed
    if module.params['state'] == 'absent':
        if account:
            if module.check_mode:
                return_changed(module)
            delete_body = {
                'id': module.params['id'],
            }
            path = '/cloud_access_providers/' + module.params['provider'] + '/accounts'
            delete = client.delete(path, data=delete_body)
            if delete.status_code != 204:
                module.fail_json(msg="Failed to delete provider account")
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.exit_json(**result)

    # Create account if missing
    if not account:
        if module.check_mode:
            return_changed(module)
        new_account = [
            {
                'id': module.params['id'],
                'nickname': module.params['nickname'],
            }
        ]
        path = '/cloud_access_providers/' + module.params['provider'] + '/accounts'
        create = client.post(path, data=new_account)
        if create.status_code != 204:
            module.fail_json(msg="Failed to create provider account")
        result['changed'] = True
        account = new_account
    else:
        # Update existing account if nickname is different and was not autocreated by Cloud Sources
        if module.params['nickname'] and account['nickname'] != 'Created by Sources' and module.params['nickname'] != account['nickname']:
            if module.check_mode:
                return_changed(module)
            updated_account = {'nickname': module.params['nickname']}
            path = '/cloud_access_providers/' + module.params['provider'] + '/accounts/' + account['id']
            update = client.put(path, data=updated_account)
            if update.status_code != 204:
                module.fail_json(msg="Failed to update provider account")
            result['changed'] = True

    # Submit an account verification if provided and account is not already verified
    if module.params['verification_identity'] and ('verified' not in account or not account['verified']):
        if module.check_mode:
            return_changed(module)
        # The API expects identity and signature to be base64 encoded
        # Because base64.b64encode returns values as bytes, we decode it back to a string
        verification = {
            'identity': module.params['verification_identity'],
            'signature': module.params['verification_signature'],
        }

        if module.params['provider'] == "GCE":
            del verification['signature']

        path = '/cloud_access_providers/' + module.params['provider'] + '/accounts/' + module.params[
            'id'] + '/verification'
        verify = client.put(path, data=verification)
        if verify.status_code != 204:
            module.fail_json(msg=f'Failed to verify provider account ${verify.status_code}')
        result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
