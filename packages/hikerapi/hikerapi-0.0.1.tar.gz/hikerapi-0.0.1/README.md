# Hikerapi client, for Python 3

[![Package](https://github.com/Hikerapi/hikerapi-python/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/Hikerapi/hikerapi-python/actions/workflows/python-package.yml)
![PyPI](https://img.shields.io/pypi/v/hikerapi)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hikerapi)

[![Downloads](https://pepy.tech/badge/hikerapi)](https://pepy.tech/project/hikerapi)
[![Downloads](https://pepy.tech/badge/hikerapi/month)](https://pepy.tech/project/hikerapi)
[![Downloads](https://pepy.tech/badge/hikerapi/week)](https://pepy.tech/project/hikerapi)


## Installation

```
pip install hikerapi
```

## Usage

Create a token https://hikerapi.com/tokens and copy "Access key"

```python
from hikerapi import Client

cl = Client(token="<ACCESS_KEY>")
user = cl.user_by_username_v2("instagram")
print(user)
```

```python
from hikerapi import AsyncClient

cl = AsyncClient(token="<ACCESS_KEY>")
user = await cl.user_by_username_v2("instagram")
print(user)
```

## Run tests

```
HIKERAPI_TOKEN=<token> pytest -v tests.py

HIKERAPI_TOKEN=<token> pytest -v tests.py::test_search_music
```
