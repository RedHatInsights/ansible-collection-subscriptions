auto_registration_verification
==============================

This role runs against an AWS EC2 instance or Azure VM to verify a cloud provider account
for use with RHSM auto registration. Once an account has been verified, subscription-manager
can automatically register a cloud system to your Red Hat account.

This role only needs to be run one time against any Linux instance in a cloud provider account
to allow auto registration for all RHEL instances in the same account.

Requirements
------------

This role requires the `requests-oauthlib` Python library.

Role Variables
--------------

| Variable                    | Required | Default         | Choices   | Comments                                 |
|-----------------------------|----------|-----------------|-----------|------------------------------------------|
| auto_registration_provider  | no       | (auto-detected) | AWS, MSAZ | The cloud provider for the VM. This is usually auto-detected using Ansible facts and only needs to be manually set if auto-detection fails. |
| rh_api_refresh_token        | yes      |                 |           | Offline refresh token for authenticating with Red Hat APIs. This can be obtained from [access.redhat.com](https://access.redhat.com/management/api) |
| rh_api_refresh_token_client | no       | rhsm-api        |           | OAuth client ID used for refreshing token |

Example Playbook
----------------

```yaml
- hosts: all
  roles:
    - role: auto_registration_verification
      vars:
        rh_api_refresh_token: aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1kUXc0dzlXZ1hjUQo=
```

License
-------

Apache 2.0

Author Information
------------------

Red Hat, Inc.
