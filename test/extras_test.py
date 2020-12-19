"""
This tests extras_require feature of setuptools.

We declared isort[pyproject], which requires the toml module.
We wouldn't have that module otherwise.

We also declared google-cloud-logging which requires
google-api-core[grpc], which in turn requires the grpcio (grpc) model.
This is a second-order-dependency test.
"""

import toml
import grpc
