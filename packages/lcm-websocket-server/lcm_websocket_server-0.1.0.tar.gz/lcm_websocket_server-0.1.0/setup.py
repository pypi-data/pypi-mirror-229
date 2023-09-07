# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lcm_websocket_server']

package_data = \
{'': ['*']}

install_requires = \
['websockets>=10.4,<11.0']

entry_points = \
{'console_scripts': ['lcm-websocket-server = lcm_websocket_server.app:main']}

setup_kwargs = {
    'name': 'lcm-websocket-server',
    'version': '0.1.0',
    'description': 'WebSocket server for republishing LCM messages',
    'long_description': '# lcm-websocket-server\n\nWebSocket server for republishing LCM messages.\n\n## Installation\n\n```bash\npoetry build\npip install dist/lcm_websocket_server-*-py3-none-any.whl\n```\n\n## Usage\n\nFor a list of available options, run:\n```bash\nlcm-websocket-server --help\n```\n\nTo run the server locally on port 8765 and republish messages on all channels:\n```bash\nlcm-websocket-server --host localhost --port 8765 --channel ".*" your_lcm_types_package\n```\n\nThe `lcm_packages` argument is the name of the package (or comma-separated list of packages) that contains the LCM Python message definitions. Submodules are scanned recursively and registered so they can be automatically identified, decoded, and republished. \n\n### Example: `compas_lcmtypes`\n\nFor example, the `compas_lcmtypes` package contains LCM types for the CoMPAS lab. These can be installed with:\n```bash\npip install compas-lcmtypes==0.1.0\n```\n\nThen, the server can be run with:\n```bash\nlcm-websocket-server compas_lcmtypes\n```\n\n## Docker\n\n### Build\n\nA Docker image to run the `lcm-websocket-server` can be built with:\n\n```bash\n./scripts/docker_build.sh\n```\n\nThis will create the `mbari/lcm-websocket-server` image.\n\n### Run\n\nThe container can be run with:\n\n```bash\ndocker run \\\n    --name lcm-websocket-server \\\n    --rm \\\n    -e HOST=0.0.0.0 \\\n    -e PORT=8765 \\\n    -e CHANNEL=".*" \\\n    -v /path/to/your_lcm_types_package:/app/your_lcm_types_package \\\n    -e LCM_PACKAGES=your_lcm_types_package \\\n    --network=host \\\n    -d \\\n    mbari/lcm-websocket-server\n```\n\nNote that the `HOST`, `PORT`, and `CHANNEL` environment variables specified above are the defaults for the `mbari/lcm-websocket-server` image. These can be omitted if the defaults are acceptable.\n\nThe `LCM_PACKAGES` environment variable should be set to the name of the package (or comma-separated list of packages) that contains the LCM Python message definitions. The `/app` directory is included in the `PYTHONPATH` so that any packages mounted there (as shown with `-v` above) can be imported.\n\nIt\'s recommended to run with `--network=host` to avoid issues with LCM over UDP. This will allow the container to use the host\'s network stack.\n',
    'author': 'Kevin Barnard',
    'author_email': 'kbarnard@mbari.org',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
