# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spackle', 'spackle.stores']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.31.0,<3.0.0', 'six>=1.16.0,<2.0.0', 'stripe>=5.2.0,<6.0.0']

setup_kwargs = {
    'name': 'spackle-python',
    'version': '0.0.44b1',
    'description': '',
    'long_description': '# Spackle Python Library\n\n[![CI](https://github.com/spackleso/spackle-python/actions/workflows/test.yml/badge.svg)](https://github.com/spackleso/spackle-python/actions/workflows/test.yml) [![pypi](https://img.shields.io/pypi/v/spackle-python.svg)](https://pypi.python.org/pypi/spackle-python)\n\nThe Spackle Python library provides optimized access to billing aware flags created on the Spackle platform.\n\n## Documentation\n\nSee the [Python API docs](https://docs.spackle.so/python).\n\n## Setup\n\n### Install the Spackle library\n\n```sh\npip install -U spackle-python\n```\n\n### Configure your environment\nIn order to use Spackle, you need to configure your API key on the `spackle` module. You can find your API key in Spackle app [settings page](https://dashboard.stripe.com/settings/apps/so.spackle.stripe).\n\n```python\nimport spackle\nspackle.api_key = "<api key>"\n```\n\n## Usage\n\n### Pricing tables\n\n#### Fetch a pricing table\n\n```python\npricing_table = spackle.PricingTable.retrieve("abcde123")\n```\n\n#### Pricing table object\n```ts\n{\n  id: string\n  name: string\n  intervals: string[]\n  products: {\n    id: string\n    features: {\n      id: string\n      name: string\n      key: string\n      type: number\n      value_flag: boolean\n      value_limit: number | null\n    }[]\n    name: string\n    prices: {\n      month?: {\n        unit_amount: number\n        currency: string\n      }\n      year?: {\n        unit_amount: number\n        currency: string\n      }\n    }\n  }[]\n}\n```\n\n### Entitlements\n\n#### Fetch a customer\n\nSpackle uses stripe ids as references to customer features.\n\n```python\ncustomer = spackle.Customer.retrieve("cus_00000000")\n```\n\n#### Verify feature access\n\n```python\ncustomer.enabled("feature_key")\n```\n\n#### Fetch a feature limit\n\n```python\ncustomer.limit("feature_key")\n```\n\n#### Examine a customer\'s subscriptions\n\nA customer\'s current subscriptions are available on the `subscriptions` property. These are valid `stripe.Subscription` objects as defined in the [Stripe Python library](https://stripe.com/docs/api/subscriptions/object?lang=python).\n\n```python\ncustomer.subscriptions\n```\n\n#### Waiters\n\nThere is a brief delay between when an action takes place in Stripe and when it is reflected in Spackle. To account for this, Spackle provides a `waiters` module that can be used to wait for a Stripe object to be updated and replicated.\n\n1. Wait for a customer to be created\n   ```python\n   spackle.wait_for_customer("cus_00000000")\n   ```\n2. Wait for a subscription to be created\n   ```python\n   spackle.wait_for_subscription("cus_000000000", "sub_00000000")\n   ```\n3. Wait for a subscription to be updated\n   ```python\n   spackle.wait_for_subscription("cus_000000000", "sub_00000000", status="active")\n   ```\n\nThese will block until Spackle is updated with the latest information from Stripe or until a timeout occurs.\n\n#### Usage in development environments\n\nIn production, Spackle requires a valid Stripe customer. However, that is not development environments where state needs to be controlled. As an alternative, you can use a file store to test your application with seed data.\n\n```json\n/app/spackle.json\n\n{\n  "cus_000000000": {\n    "features": [\n      {\n        "type": 0,\n        "key": "flag_feature",\n        "value_flag": true\n      },\n      {\n        "type": 1,\n        "key": "limit_feature",\n        "value_limit": 100\n      }\n    ],\n    "subscriptions": [\n      {\n        "id": "sub_000000000",\n        "status": "trialing",\n        "quantity": 1\n      }\n    ]\n  }\n}\n```\n\nThen configure the file store in your application:\n\n```python\nspackle.set_store(spackle.FileStore("/app/spackle.json"))\n```\n\n\n## Usage in testing environments\n\nIn production, Spackle requires a valid Stripe customer. However, that is not ideal in testing or some development environments. As an alternative, you can use an in-memory store to test your application with seed data.\n\n```python\nspackle.set_store(spackle.MemoryStore())\nspackle.get_store().set_customer_data("cus_000000000", {\n  "features": [\n    {\n      "type": 0,\n      "key": "flag_feature",\n      "value_flag": True,\n    },\n    {\n      "type": 1,\n      "key": "limit_feature",\n      "value_limit": 100,\n    },\n  ],\n  "subscriptions": [\n     {\n       "id": "sub_000000000",\n       "status": "trialing",\n       "quantity": 1,\n     }\n  ]\n})\n```\n\n**Note:** The in-memory store is not thread-safe and state will reset on each application restart.\n\n## Logging\nThe Spackle Python library emits logs as it performs various internal tasks. You can control the verbosity of Spackle\'s logging a few different ways:\n\n1. Set the environment variable SPACKLE_LOG to the value `debug`, `info`, or `warn`\n\n   ```sh\n   $ export SPACKLE_LOG=debug\n   ```\n\n2. Set spackle.log:\n\n   ```python\n   import spackle\n   spackle.log = \'debug\'\n   ```\n\n3. Enable it through Python\'s logging module:\n\n   ```python\n   import logging\n   logging.basicConfig()\n   logging.getLogger(\'spackle\').setLevel(logging.DEBUG)\n   ```\n\n',
    'author': 'Hunter Clarke',
    'author_email': 'hunter@spackle.so',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
