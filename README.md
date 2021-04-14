# Ansible Collection for cloud.redhat.com Subscriptions

This repo hosts the `redhatinsights.subscriptions` Ansible Collection.

The is a growing collection of modules and roles to help manage Red Hat subscriptions and access content.

## Included content

Click on the name of a plugin or module to view that content's documentation:

  - **Connection Plugins**:
  - **Filter Plugins**:
  - **Inventory Source**:
  - **Lookup Plugins**:
  - **Modules**:
    - [cloud_provider_account](plugins/modules/cloud_provider_account.py)
  - **Roles**:
    - [auto_registration_verification](roles/auto_registration_verification)
 
## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using this collection, you need to install it with the Ansible Galaxy CLI:

    ansible-galaxy collection install redhatinsights.subscriptions

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: redhatinsights.subscriptions
    version: main
```

### Installing required libraries

Content in this collection requires the [requests-oauthlib](https://pypi.org/project/requests-oauthlib/) to handle authentication with Red Hat APIs. You can install it with:

    pip3 install requests-oauthlib

## License

Apache 2.0

See LICENCE to see the full text.
