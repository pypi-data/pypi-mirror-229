# Simplify how you read configuration files using PyYAML
[![codecov](https://codecov.io/gh/EM51641/PyYAMEL-object/graph/badge.svg?token=OxgVmDwXah)](https://codecov.io/gh/EM51641/PyYAMEL-object)  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![PyPI](https://img.shields.io/pypi/v/pyaml-object)](https://pypi.org/project/pyaml-object) [![Python](https://img.shields.io/pypi/pyversions/pyaml-object)](https://pypi.org/project/pyaml-object) [![Unit Tests](https://github.com/EM51641/PyYAMEL-object/actions/workflows/unit.yaml/badge.svg)](https://github.com/EM51641/PyYAMEL-object/actions/workflows/unit.yaml)


Having a ```service.yaml``` file such:
```yaml
service:
    version: 1.0.0
    name: myservice
    secret_key: XXXXXX
```

We can read the config file through the Config API by applying the read method.

```python
from pyyaml_object.config import Config
conf_manager = Config('service.yaml')
conf = conf_manager.read()
```

Now we have a ```conf``` object that embedes every key and value from our yaml file. For instance, we can reconstitute a constant ```SETTING``` variable such:

```python
SETTINGS = {
    'VERSION': conf.service.version,
    'NAME': conf.service.name,
    'SECRET_KEY': conf.service.secret_key
}

print(SETTINGS)
#{'VERSION': '1.0.0', 'NAME': 'myservice', 'SECRET_KEY': 'XXXXXX'}
```