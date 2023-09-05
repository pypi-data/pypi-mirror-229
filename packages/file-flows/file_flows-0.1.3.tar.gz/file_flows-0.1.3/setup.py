# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['file_flows']

package_data = \
{'': ['*']}

install_requires = \
['polars[all]>=0.17.2,<0.18.0',
 'pyarrow>=11.0.0,<12.0.0',
 'pydantic-settings>=2.0.3,<3.0.0',
 'pydantic>=2.3.0,<3.0.0',
 's3fs[boto3]>=2023.4.0,<2024.0.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'file-flows',
    'version': '0.1.3',
    'description': 'A single high-level file operations API for both object stores and local file system.',
    'long_description': 'Core functions are accessed through the `FileOps` class. This is a high-level interface for file operations on your local file system and/or s3 protocol object stores. Internally, appropriate functions will by called based on the type of arguments passed. i.e. `s3://` path or `/local/path`.\n\n```py\nfrom file_flows import FileOps\n```\nCore functions include `create, transfer, copy, move, delete, exists, file_size, list_files, parquet_column_names, df_from_csv, df_from_parquet`.\nSee [core](/file_flows/core.py) for more details.   \n\nAdditional functionality specific to s3 protocol object stores can be accessed through the `S3Ops` class. See [s3](/file_flows/s3.py) for more details.\n```py\nfrom file_flows import S3Ops\n```\n\nBoth `FileOps` and `S3Ops` take an optional `S3Cfg` object as argument (`from file_flows import S3Cfg`). `S3Cfg` contains parameters for the s3 protocol object store you are working with. If no argument is provided, `S3Cfg` will default to environment variables: `s3_endpoint_url` (http://localhost:9000 by default), `aws_access_key_id`, `aws_secret_access_key`.',
    'author': 'Dan Kelleher',
    'author_email': 'kelleherjdan@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/djkelleher/file-flows',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
