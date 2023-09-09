# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flow_client',
 'flow_client.flow_cli',
 'flow_client.flow_cli.commands',
 'flow_client.flow_cli.utils',
 'flow_sdk',
 'flow_sdk.client',
 'flow_sdk.client.api',
 'pipeline',
 'pipeline.backend',
 'pipeline.component',
 'pipeline.component.nn',
 'pipeline.component.nn.backend',
 'pipeline.component.nn.backend.torch',
 'pipeline.component.nn.models',
 'pipeline.demo',
 'pipeline.interface',
 'pipeline.param',
 'pipeline.parser',
 'pipeline.runtime',
 'pipeline.test',
 'pipeline.utils',
 'pipeline.utils.invoker']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'loguru>=0.6.0',
 'pandas>=1.1.5',
 'poetry>=0.12',
 'requests>=2.24.0,<3.0.0',
 'requests_toolbelt>=0.9.1,<0.10.0',
 'ruamel.yaml>=0.16.10,<0.17.0',
 'setuptools>=65.5.1']

entry_points = \
{'console_scripts': ['flow = flow_client.flow:flow_cli',
                     'pipeline = pipeline.pipeline_cli:cli']}

setup_kwargs = {
    'name': 'fate-client',
    'version': '1.11.3',
    'description': 'Clients for FATE, including flow_client and pipeline',
    'long_description': '# fate client\n',
    'author': 'FederatedAI',
    'author_email': 'contact@FedAI.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://fate.fedai.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
